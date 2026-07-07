# 고래상사 리워크 — 로드맵 (2026-07-07 기준)

> 이 문서는 리워크가 운영(goraesangsa.com)을 대체하는 순간(cutover)까지, 그리고 그 이후의
> 전체 계획이다. 각 단계는 선행조건·실행자(사용자/Claude)·검증 방법을 함께 적는다.
> 진행하면서 체크박스를 갱신할 것.

---

## 0. 현재 상태 스냅샷

### 완료된 것
- **18페이지 실구현** (홈 + 하위 17): crew/members/member, archive(+detail), clips(+clip),
  schedule(+detail), multiview, notices(+notice), news, admin 5종. 커밋 `831d30b`.
- **Phase A — SOOP 로그인 CRUD** (2026-07-02): 공지·클립·일정·아카이브 4종.
  세션 `sessionStorage.soop_user={id,nickname,role}`, `WhaleUI`/`WhaleData`,
  데이터는 `/rework/*`로 격리. 추가=로그인, 수정삭제=본인 것(soop id), 아카이브=관리자 전용.
- **Phase B — 서버 강제** (2026-07-07, 커밋 `63bb07c`):
  - 워커 `POST /auth/firebase` (whale-status-worker.kyefyx.workers.dev):
    SOOP 토큰 검증 → `/permissions/{닉}` 조회 → uid=soop user_id, admin claim RS256 커스텀토큰.
    secrets: `FIREBASE_SA_EMAIL`, `FIREBASE_SA_KEY`.
  - Firebase: 웹앱 등록(웹 API 키 `AIzaSyBZpdQES1EeZLieWiRwo-sNrA2wJQ6vZ9k`, 공개키),
    Authentication 활성화(안 하면 `CONFIGURATION_NOT_FOUND`).
  - 클라: `auth/callback.html`이 커스텀토큰→idToken 교환해 `sessionStorage.soop_fb` 저장,
    `assets/site.js`의 WhaleData가 쓰기 URL에 `?auth=idToken` 첨부 + 만료 1분 전 자동 refresh.
  - RTDB 규칙 게시(`src/firebase-rules.json`): `/rework` 공개쓰기 제거,
    소유권(ownerId=uid)·관리자(admin claim) 서버 강제. **검증 매트릭스 11/11 PASS.**

### 현재 제약 (의도된 상태)
- SOOP OAuth redirect_uri가 `https://www.goraesangsa.com/auth/callback` 고정
  → **리워크 오리진(GitHub Pages)에서는 실로그인 불가 → 편집 기능은 cutover까지 잠김.**
  dev 로그인은 idToken이 없어 쓰기 시 401 (정상 동작).
- 워커 CORS `ALLOWED_ORIGIN`도 goraesangsa.com 전용.

### 인프라 실측 (2026-07-07 확인)
- **운영 호스팅 = Vercel** (`vercel.json` cleanUrls:true, 응답헤더 server: Vercel).
- 운영 RTDB `/schedules`에 실데이터 존재 (운영 일정 관리 시스템이 사용 중).
- `/rework` 하위엔 현재 `contests`, `notices`만 존재 (클립·일정 시드는 미이관).
- 레포: `github.com/HotCake0/Test_version` (로컬 브랜치명 `Test_version` →
  푸시는 `git push origin Test_version:main`).

---

## 1. 즉시 뒷정리 — 보안 (cutover와 무관, 빠를수록 좋음)

- [ ] **1-1. 서비스계정 키 교체** (실행자: 사용자, ~5분)
  - 사유: 현재 키(`04cee49a...`)의 private_key가 채팅에 노출됐고 다운로드 폴더에 JSON이 남음.
  - 절차: Firebase 콘솔 → 프로젝트 설정 → 서비스 계정 → "Google Cloud에서 서비스 계정 관리"
    → `firebase-adminsdk-fbsvc@...` 계정 → 키 탭 → `04cee49a...` 삭제 → "키 추가 > 새 키(JSON)"
    → Cloudflare whale-status-worker의 `FIREBASE_SA_KEY` secret 값만 새 private_key로 교체.
    (`FIREBASE_SA_EMAIL`은 동일하므로 그대로. 코드 변경 없음.)
  - 검증(Claude): 가짜 토큰으로 `/auth/firebase` 400 응답 확인 + 새 키 기준 교환 테스트.
  - ⚠️ 순서 주의: **새 키를 secret에 넣은 다음** 옛 키를 삭제해야 무중단.
- [ ] **1-2. 다운로드 폴더의 키 JSON 삭제** (실행자: 사용자)
  - `C:\Users\kyefy\Downloads\whaie-corp-firebase-adminsdk-fbsvc-*.json`
- [ ] **1-3. (선택) 로컬 브랜치명 정리**: `git branch -m Test_version main` +
  `git push -u origin main` + 옛 추적 정리. 이후 푸시가 그냥 `git push`로 단순해짐.

---

## 2. Cutover 전 준비 — 콘텐츠·품질

### 2-A. 콘텐츠 실데이터화
- [ ] **2-A-1. 멤버 직책/부서/스탯 확정** (사용자 확인 필요)
  - 현재 `src/content/members.json`의 직책·부서·스탯은 역할극 테마 placeholder.
  - 운영본 조직도(index.html) 기준으로 실제 직급(사장/부사장/부장/사원)·부서 반영.
  - 수정 위치: `src/content/members.json` → `python3 src/build.py` 재생성.
- [ ] **2-A-2. 클립 실데이터**: 시드 12개(`src/content/clips.json`)를 실제 SOOP VOD/유튜브
  클립으로 교체. 방법 2가지 중 택1:
  (a) 시드 JSON을 실클립으로 갱신해 두고 cutover 후 관리자 "시드 불러오기"로 이관,
  (b) cutover 후 관리자 로그인으로 UI에서 직접 입력.
  ※ `/rework/clips`가 현재 비어 있으므로 어느 쪽이든 충돌 없음.
- [ ] **2-A-3. 공지 실데이터**: `/rework/notices`에 시드가 이미 이관돼 있음.
  실공지로 정리(관리자 편집은 cutover 후 가능, 급하면 Claude가 서비스계정 토큰으로 대행 가능).
- [ ] **2-A-4. 일정 데이터 정책 결정** (⭐ 설계 결정 — §3-C와 연동)
  - 운영 `/schedules`(실데이터, 기존 admin.js 일정 시스템이 관리)와
    리워크 `/rework/schedules`(CRUD 시드)가 이원화되어 있음.
  - 후보: ① cutover 때 운영 `/schedules` → `/rework/schedules` 1회 이관 후 리워크 CRUD가 정식
    ② 리워크 schedule 페이지가 운영 `/schedules`를 읽도록 변경(기존 admin 시스템 유지)
  - 권장 ①: 일정도 소유권/권한 강제를 받게 되고 시스템이 하나로 통일됨.
    이관 스크립트는 Claude가 작성(형식 변환: 운영 스키마 → 리워크 스키마 매핑 필요).
- [ ] **2-A-5. 뉴스 피드 확인**: news.html은 공지+클립+일정 통합 피드라 소스가 채워지면 자동.

### 2-B. 품질 점검
- [ ] **2-B-1. 모바일/반응형 실기기 점검** (사용자 — 메모리 방침: UI 확인은 사용자가)
  - 체크: 가로핀 섹션 모바일 폴백, 드로어, 카드 그리드, 모달 폼 입력.
- [ ] **2-B-2. reduced-motion 동작 확인** (Claude가 Playwright로 가능)
- [ ] **2-B-3. SEO/메타**: 페이지별 `<title>`/`og:title`/`og:image`/파비콘/`meta description`.
  build.py의 head partial에서 일괄 처리. (Claude)
- [ ] **2-B-4. 404 페이지·잘못된 `?id=` 접근 처리 확인** (상세페이지 폴백 이미 있음, 재확인만)
- [ ] **2-B-5. 이미지 용량 점검**: img/ 20장 중 대형 파일 압축(품질 유지 범위). (Claude)
- [ ] **2-B-6. 콘솔 에러 0 확인**: 전 페이지 Playwright 순회. (Claude)

---

## 3. Cutover 설계 — 사전 결정사항

### 3-A. 배포 방식 결정 (⭐ 최우선 확인 필요)
- **확인 필요(사용자)**: goraesangsa.com이 연결된 **Vercel 프로젝트가 누구 계정**이며,
  **어느 GitHub 레포**를 배포 중인가? (운영 코드 폴더는 `Whale-Corp-main`이지만
  연결 레포/계정은 미확인 — 친구 계정일 가능성 있음.)
- 후보:
  - **① Vercel 프로젝트의 연결 레포를 Test_version으로 교체** (또는 Test_version을 새 Vercel
    프로젝트로 만들고 도메인만 이전) — 리워크 레포가 그대로 정식이 됨. 권장.
  - ② 운영 레포에 리워크 산출물을 복사해 푸시 — 레포 이원화가 남아 관리 복잡. 비권장.
- 참고: 리워크는 순수 정적 사이트라 Vercel 설정은 `vercel.json {"cleanUrls": true}` 정도면 충분.
  cleanUrls 사용 시 내부 링크 `.html` 확장자 정리 여부 검토(현재 리워크 링크는 `.html` 포함 —
  cleanUrls는 확장자 있는 접근도 리다이렉트로 처리하므로 동작엔 문제없음).

### 3-B. URL/경로 호환
- 운영 URL: `/index.html`, `/CCTV.html`, `/schedule.html`, `/ranking.html`, `/contest.html`,
  `/admin.html` (+cleanUrls로 확장자 없는 형태 유통 가능).
- 리워크 URL: `/index.html`, `/pages/*.html`.
- [ ] 결정: 옛 URL → 새 URL **리다이렉트 맵** 작성 (vercel.json `redirects`).
  예: `/CCTV` → `/pages/multiview`, `/schedule` → `/pages/schedule`,
  `/contest` → `/pages/archive`, `/ranking` → `/pages/archive`(또는 통계 페이지 후속),
  `/admin` → `/pages/admin`.
- [ ] `auth/callback.html` 경로는 운영과 동일(`/auth/callback`)이라 SOOP 앱 설정 변경 불필요.
  단, **www 여부 일치** 확인: redirect_uri가 `https://www.goraesangsa.com/...`이므로
  Vercel에서 www를 정식으로 두고 apex→www 리다이렉트 유지.

### 3-C. 데이터 경로 정책 (⭐ 설계 결정)
- 후보:
  - **① `/rework/*`를 그대로 정식 경로로 사용** — 코드·규칙·데이터 무변경, 즉시 안정.
    이름이 어색할 뿐 기능 문제 없음. **권장(1차 cutover 시)**.
  - ② `/rework/*` → `/v2/*` 등으로 개명 이전 — 서비스계정 스크립트로 데이터 복사 + site.js
    `REWORK_BASE` 변경 + 규칙 이동. 미관용. cutover가 안정된 뒤 여유 있을 때만.
- [ ] 아카이브 데이터 최신화: cutover 직전에 운영 `/contests` → `/rework/contests` **재이관**
  (Phase A의 관리자 "불러오기"는 목록이 빌 때만 동작하므로, 이미 데이터가 있으면
  Claude가 서비스계정 토큰으로 diff 이관 스크립트 실행).
- [ ] 일정 데이터 이관(§2-A-4 결정에 따름).

### 3-D. 운영 전용 기능 인수인계 확인
- [ ] **ranking.html(대회 통계)**: 리워크에 대응 페이지 없음 → archive에 흡수됐는지 확인,
  부족하면 통계 섹션 후속 개발 목록에 등재.
- [ ] **admin.html(기존 관리자: 일정/대회 CRUD)**: 리워크 admin-*는 데모 목업 상태.
  일정·아카이브 CRUD는 이미 각 페이지 인라인 편집으로 대체됨 → 기존 admin의 나머지 기능
  (기간 반복 일정 등) 필요 여부 사용자 결정.
- [ ] **image-protect.js(우클릭 방지)**: 리워크에 미적용 — 적용 여부 사용자 결정.
- [ ] **워커 cron(5분 status 갱신)**: 그대로 유지 (리워크 멀티뷰/멤버가 동일 `/status` 사용).

---

## 4. Cutover 실행 체크리스트 (D-Day)

> 예상 소요 1~2시간. 문제 시 롤백 지점 명확히.

1. [ ] **백업**: 운영 레포 태그(`prod-final-YYYYMMDD`) + RTDB 전체 export
   (콘솔 → 데이터 탭 → JSON 내보내기, 또는 Claude가 서비스계정으로 `/.json` 덤프).
2. [ ] **데이터 최신화**: §3-C의 contests 재이관 + 일정 이관 실행. (Claude)
3. [ ] **배포 전환**: §3-A 결정대로 Vercel 연결 교체 → goraesangsa.com이 리워크를 서빙.
   vercel.json(리다이렉트 맵 포함)은 사전에 레포에 커밋해 둠. (사용자+Claude)
4. [ ] **스모크 테스트** (Claude, curl+Playwright):
   - 전 페이지 HTTP 200, 콘솔 에러 0, 옛 URL 리다이렉트 동작.
   - `/auth/callback` 접근 가능(200) 확인.
5. [ ] **실로그인 검증** (사용자):
   - 관리자 계정 SOOP 로그인 → 공지 작성/수정/삭제 + 아카이브 편집 + pinned/featured 토글.
   - 일반 계정(권한 없는 SOOP 계정) 로그인 → 본인 글만 수정 가능, 남의 글 버튼 미노출,
     (개발자도구로 강제 호출해도 401 — Claude가 안내하는 콘솔 스니펫으로 확인 가능).
6. [ ] **모니터링 개시**: 첫 24시간 집중(로그인 실패/쓰기 401 오탐/멀티뷰 status 갱신),
   이후 1주 관찰. 문제 기준: 로그인 불가, 데이터 유실, 주요 페이지 백지.
7. [ ] **롤백 계획**: Vercel에서 이전 배포로 즉시 롤백 가능(Instant Rollback) +
   연결 레포 원복. RTDB는 1번 백업본으로 복원.
8. [ ] **사후 정리** (안정 확인 후, ~1주 뒤):
   - [ ] 리워크 편집 잠김 해제 확인(자연 해소)로 공지/클립 실콘텐츠 입력 마저 진행.
   - [ ] 옛 운영 코드 아카이브(`Whale-Corp-main` → 보존 폴더), `리워크폐기/` 정리.
   - [ ] README 갱신(레포가 이제 정식 운영 코드임을 명시).

---

## 5. Cutover 후 백로그 (우선순위순)

### 5-1. 운영 데이터 경로 보안 강제 (Phase C — 권장)
현재 운영 경로(`status`/`contests`/`schedules`/`crews`)는 여전히 공개쓰기. cutover 후:
- `contests`·`schedules`·`crews`: 리워크 CRUD(idToken)로만 쓰게 됐다면
  `/rework`와 같은 규칙으로 조임 (또는 §3-C-②로 통합 후 옛 경로 `.write:false`).
- `status`: **워커만** 쓰는 경로. 워커가 Google OAuth2 서비스계정 access token
  (scope: `https://www.googleapis.com/auth/firebase.database` + userinfo.email)을 발급받아
  `?access_token=`으로 쓰도록 변경 → 규칙 `.write:false`(서비스계정은 규칙 우회. 관리자 권한).
  WebCrypto JWT 서명은 이미 워커에 있으므로 aud만 `https://oauth2.googleapis.com/token`으로
  바꾼 assertion 추가 구현이면 됨. (Claude 구현 가능, 워커 재배포 1회)
- `permissions`: 현행 유지(`.write:false`, 콘솔에서만 수정).

### 5-2. 규칙 정제
- pinned(공지)·featured(클립)를 비관리자가 못 바꾸게 `.validate` 추가:
  `newData.child('pinned').val() === data.child('pinned').val() || auth.token.admin === true` 계열.
  (현재는 클라 게이팅만 — 악의적 owner가 자기 글을 pinned로 만들 수 있는 작은 구멍.)
- 필드 스키마 validate(제목 길이, url 스킴 `https?://` 서버측 검증 등).

### 5-3. 관리자 페이지 실연동
- admin-clips/notices/members 테이블(현재 데모 alert)을 WhaleData 실 CRUD로.
- 기간 반복 일정(옛 admin.js groupId 기능) 이식 여부 결정.
- permissions 관리 UI(관리자가 콘솔 없이 admin/editor 지정) — 규칙상 콘솔 전용이므로
  워커 경유 API(admin claim 검증 후 서비스계정으로 쓰기) 필요. 중기 과제.

### 5-4. 기능/콘텐츠 개선
- 대회 통계 페이지(옛 ranking.html의 참여율/승률) 리워크 디자인으로 재구현.
- LIVE "지금 방송 중" 그리드 섹션 재도입 검토(과거 한 번 제거, 사용자 재요청 가능성).
- 멤버 스탯 실데이터화(방송 시간·팔로워 등 SOOP API 연동 검토).
- 클립 유튜브/SOOP 임베드 플레이어(현재 링크만).

### 5-5. 운영 위생
- RTDB 정기 백업 자동화(워커 cron으로 주 1회 `/.json` 덤프 → GitHub/Drive).
- 서비스계정 키 로테이션 주기(연 1회 권장) 및 절차 문서화(§1-1과 동일).
- Firebase App Check 검토(봇 남용 방지 — 정적 사이트라 reCAPTCHA 기반).
- Lighthouse 성능/접근성 정기 점검.

---

## 6. 미확인 항목 (다음 세션에서 사용자에게 물어볼 것)

| # | 질문 | 영향 |
|---|---|---|
| 1 | goraesangsa.com Vercel 프로젝트의 소유 계정·연결 레포? | §3-A 배포 전환 방식 |
| 2 | 일정 시스템 통합 방향(①리워크로 통일 vs ②기존 유지)? | §2-A-4, §3-C |
| 3 | 멤버 실제 직급/부서 확정본? | §2-A-1 |
| 4 | ranking(통계)·기간반복일정·이미지보호 인수 여부? | §3-D |
| 5 | cutover 희망 시기? | §4 일정 |

---

## 부록 A. 아키텍처 요약 (현재)

```
[브라우저]
  ├─ 정적 페이지: pages/*.html (산출물, 수정은 src/build.py에!)
  ├─ 공유: assets/site.css, assets/site.js (WhaleUI 권한게이팅 / WhaleData CRUD)
  ├─ 로그인: SOOP OAuth → auth/callback.html
  │     └ 워커 /auth/token(code교환) → /auth/firebase(커스텀토큰) → idToken 교환·저장
  └─ 쓰기: WhaleData.create/update/remove → RTDB /rework/*?auth=idToken

[Cloudflare Worker: whale-status-worker.kyefyx.workers.dev]
  ├─ /auth/token, /auth/me, /auth/firebase(신규), /search/bj
  ├─ cron 5분: SOOP 라이브 조회 → RTDB /status
  └─ secrets: SOOP_CLIENT_SECRET, FIREBASE_SA_EMAIL, FIREBASE_SA_KEY / vars: FIREBASE_URL

[Firebase RTDB: whaie-corp (asia-southeast1)]
  ├─ 운영: /status /contests /schedules /crews (.write:true — Phase C에서 조임)
  ├─ /permissions/{닉} = "admin"|"editor" (.write:false)
  └─ /rework/{notices,clips,schedules,contests} — 규칙 강제(소유권/관리자), src/firebase-rules.json
```

## 부록 B. 검증 도구
- 규칙 검증 매트릭스: 서비스계정 키로 임의 uid/claim 토큰 발급 →
  signInWithCustomToken → REST 쓰기 시도 11종. (2026-07-07 세션 scratchpad
  `rules-matrix.mjs` — 휘발성이므로 필요 시 재작성 요청. 시나리오는 §0 참조.)
- 로컬 미리보기: 리워크 루트에서 `python3 -m http.server 8792`. 화면 안 바뀌면 Ctrl+Shift+R.
- 빌드: `python3 src/build.py` (18페이지 재생성. pages/ 직접 수정 금지).
