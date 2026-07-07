# 고래상사 리워크 — 로드맵 v2 (2026-07-07)

> 리워크가 운영(goraesangsa.com)을 대체하는 순간(cutover)까지, 그리고 그 이후의 전체 계획.
> 각 항목에 **실행자 / 선행조건 / 절차 / 합격 기준**을 명시한다. 진행하면서 체크박스를 갱신할 것.
> v2: 데이터 스키마·URL 맵·Vercel 절차·D-Day 런북·리스크를 실측 기반으로 구체화.

---

## 0. 현재 상태 스냅샷

### 0-1. 완료된 것
| 단계 | 내용 | 커밋 |
|---|---|---|
| 18페이지 실구현 | 홈 + crew/members/member, archive(+detail), clips(+clip), schedule(+detail), multiview, notices(+notice), news, admin 5종 | `831d30b` |
| Phase A (07-02) | SOOP 로그인 CRUD 4종(공지·클립·일정·아카이브), `/rework/*` 격리, `WhaleUI`/`WhaleData`, safeUrl XSS 방어 | `63bb07c` |
| Phase B (07-07) | 커스텀토큰 서버 강제 (아래 상세) | `63bb07c` |
| 로드맵 | 이 문서 | `88562ae`~ |

**Phase B 구성** (전부 배포·검증 완료):
- 워커 `POST /auth/firebase` (`whale-status-worker.kyefyx.workers.dev`, 소스 `04_WCHP/whale-auth-worker/worker.js` — 레포 밖):
  SOOP 토큰 검증 → `/permissions/{닉}` 조회 → **uid=soop user_id, `admin` claim**(admin/editor면 true)의
  RS256 커스텀토큰을 WebCrypto로 서명. 응답 `{firebase_token, user_id, nickname, role}`.
  secrets: `SOOP_CLIENT_SECRET`, `FIREBASE_SA_EMAIL`, `FIREBASE_SA_KEY`(리터럴 `\n` 자동 복원). vars: `FIREBASE_URL`.
- Firebase: 웹앱 등록(웹 API 키 `AIzaSyBZpdQES1EeZLieWiRwo-sNrA2wJQ6vZ9k` — 공개키), Authentication 활성화
  (미활성 시 교환에서 `CONFIGURATION_NOT_FOUND`).
- 클라: `auth/callback.html` = `/auth/firebase` → `signInWithCustomToken` REST 교환 →
  `sessionStorage.soop_fb = {idToken, refreshToken, expiresAt}`. 교환 실패해도 로그인은 유지(쓰기만 거부됨).
  `assets/site.js` = `authParam()/writeUrl()`이 WhaleData 쓰기 URL에 `?auth=idToken` 첨부,
  만료 60초 전부터 `securetoken.googleapis.com/v1/token`으로 자동 refresh, 로그아웃 시 `soop_fb` 폐기.
- RTDB 규칙 게시(사본 `src/firebase-rules.json`): `/rework` 공개쓰기 제거. **검증 매트릭스 11/11 PASS**(부록 C).

### 0-2. 현재 제약 (의도된 상태)
- SOOP OAuth redirect_uri = `https://www.goraesangsa.com/auth/callback` 고정 +
  워커 CORS `ALLOWED_ORIGIN` = `https://www.goraesangsa.com`
  → **리워크 오리진에서는 실로그인 불가 → 편집 기능은 cutover까지 잠김.**
  dev 로그인은 idToken이 없어 쓰기 401(규칙이 막는 게 정상 동작).
- 운영 경로(`/status` `/contests` `/schedules` `/crews`)는 여전히 공개쓰기(`.write:true`) —
  운영본이 무토큰으로 쓰는 구조라 cutover 후 Phase C(§5-1)에서 조인다.

### 0-3. 인프라·데이터 실측 (2026-07-07 curl 확인)
- **운영 호스팅 = Vercel** (응답헤더 `server: Vercel`, `vercel.json = {"cleanUrls": true}` 단 1개 설정).
  연결된 Vercel 계정·GitHub 레포는 **미확인**(§6-Q1). 운영 코드 로컬 사본 = `04_WCHP/Whale-Corp-main/`.
- 운영 페이지 6종: `index` `CCTV` `schedule` `ranking` `contest` `admin` (+`auth/callback`).
- RTDB 현황:
  - `/schedules` **73건 실사용 중** — 스키마 `{date:"YYYY-MM-DD", event:"제목", members:[soop id...], groupId?}`.
    members 고유값 11종 실측: soop id 10종 + `"goraesangsa"`(크루 전체 태그). `groupId`=기간 반복 일정 묶음.
  - `/contests` 15건(운영) / `/rework/contests` 15건(07-02 이관 사본) — cutover 직전 diff 재이관 필요.
  - `/rework/notices` 1건 = **dev 테스트 공지**(ownerId `dev:핫케이크_`, title "테스트") → 삭제 대상(§1-4).
  - `/rework/clips`·`/rework/schedules` **비어 있음** (시드 미이관 — 실데이터 넣을 때 충돌 없음).
  - `/crews` = 상대 크루 사전 `{aliases:[], currentName}` (아카이브 상세가 참조). `/permissions` = 닉→"admin"|"editor".
- 레포: `github.com/HotCake0/Test_version`. **로컬 브랜치명 `Test_version`** → 푸시는 `git push origin Test_version:main`.

### 0-4. 리워크 데이터 스키마 (부록 B에 전체 사전)
- 시드 단일소스: `src/content/{members,clips,schedule,notices,site}.json` → `python3 src/build.py` → `pages/*.html`.
  **pages/는 산출물 — 직접 수정 금지, 수정은 build.py/JSON에만.**
- CRUD 런타임 스키마는 각 폼이 정의(부록 B). 공통 자동 필드: `ownerId, ownerNick, createdAt, updatedAt`.

---

## 1. 즉시 뒷정리 — 보안 (cutover 무관, 지금 바로)

- [ ] **1-1. 서비스계정 키 교체** — 실행자: 사용자(콘솔) + Claude(검증). 소요 ~5분.
  - 사유: 현행 키(`04cee49a...`)의 private_key가 2026-07-07 채팅에 노출됨.
  - 절차 (⚠️ **이 순서대로 해야 무중단** — 새 키 등록 후 옛 키 삭제):
    1. Firebase 콘솔 → ⚙️ 프로젝트 설정 → 서비스 계정 → "새 비공개 키 생성" → JSON 다운로드.
       (같은 서비스계정 `firebase-adminsdk-fbsvc@whaie-corp.iam.gserviceaccount.com`에 키만 추가됨)
    2. Cloudflare → Workers 및 Pages → whale-status-worker → 설정 → 변수 및 비밀 →
       `FIREBASE_SA_KEY` 편집 → 새 JSON의 `private_key` 값으로 교체(따옴표 안, `\n` 포함 그대로).
       `FIREBASE_SA_EMAIL`은 동일하므로 그대로 둠. **코드 변경·재배포 불필요**(secret 교체만으로 반영).
    3. Google Cloud 콘솔(프로젝트 설정 → 서비스 계정 → "Google Cloud에서 서비스 계정 관리") →
       firebase-adminsdk 계정 → 키 탭 → 옛 키 `04cee49a...` **삭제**.
    4. 새 JSON 파일도 secret 등록 직후 삭제(다운로드 폴더에 남기지 않기).
  - 합격 기준(Claude가 실행): ① 가짜 토큰 `POST /auth/firebase` → 400(워커 생존)
    ② 실제 커스텀토큰 플로우는 옛 키 삭제 후에도 정상(새 키로 서명되므로) — 원하면 검증 매트릭스 1·2번 재실행.
- [ ] **1-2. 현행 키 JSON 삭제** — `C:\Users\kyefy\Downloads\whaie-corp-firebase-adminsdk-fbsvc-04cee49ab6.json`.
- [ ] **1-3. (선택) 로컬 브랜치명 정리** — 실행자: Claude. 이후 `git push`만으로 푸시 가능.
  ```bash
  git branch -m Test_version main
  git fetch origin && git branch -u origin/main main
  git remote set-head origin -a
  ```
- [ ] **1-4. dev 테스트 공지 삭제** — `/rework/notices`의 "테스트" 1건(ownerId `dev:핫케이크_`).
  규칙 강제로 이제 콘솔 외엔 admin 토큰이 필요 → Claude가 서비스계정 발급 admin 토큰으로 DELETE
  (검증 매트릭스와 동일한 방식), 또는 사용자가 Firebase 콘솔 데이터 탭에서 노드 삭제.

---

## 2. Cutover 전 준비 — 콘텐츠·품질

### 2-A. 콘텐츠 실데이터화

- [ ] **2-A-1. 멤버 직책/부서 확정** — 실행자: 사용자(확정) + Claude(반영). ⭐결정 필요(§6-Q3)
  - 현재 `src/content/members.json` 16인의 `role`(직책)·`dept`(부서)·`bio`·`stats`가 역할극 placeholder.
  - 운영본 조직도가 근거: 임원(대표=울산큰고래, 부사장=견자희) / 부장(비서부 멜로딩딩·게임부 김마렌·컨텐츠부 감자가비) /
    사원·인턴 — **2026-06-08 진급 반영분(채하나·희희덕=사원)까지 포함해 최신 직급표를 사용자에게 받을 것.**
  - 반영 필드: `role`, `dept`, `rank`(정렬키: 임원0~/부장10~/사원20~/인턴30~ 등 간격 유지), `bio`, `stats`(실측 없으면 유지).
  - 절차: JSON 수정 → `python3 src/build.py` → crew/members/member 3페이지 확인.
  - 합격: members 16카드 직급 정렬 일치, member 상세 스탯/소개 어색함 없음, 홈 조직 소개와 모순 없음.
- [ ] **2-A-2. 클립 실데이터** — `/rework/clips`가 비어 있으므로 방식 자유:
  - (a) `src/content/clips.json`을 실클립(제목/제작자/SOOP VOD·유튜브 URL/날짜)으로 갱신 →
    cutover 후 관리자 "시드 불러오기" 1클릭 이관. **사전 준비 가능해서 권장.**
  - (b) cutover 후 관리자 로그인으로 UI에서 직접 입력.
  - 주의: url은 `https?://`만 통과(safeUrl) — SOOP VOD는 `https://vod.sooplive.com/player/{id}` 형식 사용.
- [ ] **2-A-3. 공지 실데이터** — §1-4 테스트 공지 삭제 후, 개시 공지(리뉴얼 안내 등) 준비.
  cutover 후 입력이 자연스러움. 급하면 Claude가 admin 토큰으로 대행 입력 가능.
- [ ] **2-A-4. 일정 데이터 통합** — ⭐결정 필요(§6-Q2). **권장 ①(리워크로 통일)** 기준 이관 설계:
  - 스키마 매핑 (운영 `/schedules` 73건 → `/rework/schedules`):

    | 운영 필드 | 리워크 필드 | 변환 |
    |---|---|---|
    | `date` "YYYY-MM-DD" | `date` | 그대로 |
    | `event` | `title` | 그대로 |
    | `members` [soop id] | `members` [멤버명] | 워커 `CREW_MEMBERS` 맵(id→명)으로 변환. `"goraesangsa"` → 16인 전원 또는 `["고래상사 전체"]` 태그(리워크 렌더 확인 후 결정) |
    | `groupId` | (버림 또는 보존) | 리워크 폼엔 없음 — 보존해도 무해하므로 **보존 권장**(후속 기간반복 기능 대비) |
    | (없음) | `time` | `""` (미상) |
    | (없음) | `type` | members 1인=개인방송, 2인 이상=합방, 전체태그=특집 등 규칙 매핑(스크립트에서) |
    | (없음) | `desc` | `""` |
    | (없음) | `ownerId/ownerNick/createdAt/updatedAt` | 서비스계정 이관 시 admin 소유로 주입(`ownerId`=관리자 soop id `bach023` 권장) |
  - 실행: Claude가 이관 스크립트 작성(admin 토큰으로 POST) → 건수 73=73 검증 → 리워크 캘린더 렌더 확인.
  - 이관 후 운영 admin.js 일정 시스템은 읽기 전용 유산이 됨(§3-D에서 인수 결정).
  - 시점: **cutover 직전**(그 사이 운영에 새 일정이 계속 추가되므로 D-Day 단계에 포함, §4-2).
- [ ] **2-A-5. 뉴스 피드** — news.html은 공지+클립+일정 통합 피드. 소스가 채워지면 자동. 별도 작업 없음(확인만).

### 2-B. 품질 점검

- [ ] **2-B-1. 모바일/반응형 실기기** — 실행자: 사용자(메모리 방침: UI 확인은 사용자).
  중점: 홈 sec02 가로핀 모바일 폴백(≤860px 세로 스택), 하위페이지 드로어, CRUD 모달 폼 입력(모바일 키보드),
  캘린더 7열 그리드 축소, 멀티뷰 iframe 그리드.
- [ ] **2-B-2. reduced-motion + 콘솔 에러 0** — 실행자: Claude(Playwright).
  19페이지 순회: HTTP 200, console error 0, `prefers-reduced-motion` 에뮬레이션 시 인트로/핀 비활성 확인.
- [ ] **2-B-3. SEO/메타 일괄** — 실행자: Claude. build.py head partial에 페이지별
  `<meta name="description">`, `og:title/description/image`(대표 이미지 1장 지정 필요), `<link rel="canonical">`.
  홈 index.html은 손수정(검증본 인라인 유지 원칙 준수 — head만 추가).
  합격: 전 페이지 meta 존재 + OG 디버거(카톡 공유 미리보기) 정상.
- [ ] **2-B-4. 이미지 최적화** — 실행자: Claude. `img/` 20장 실측 후 200KB 초과분 재압축(화질 유지),
  가능하면 `loading="lazy"` 부여(빌드 템플릿에서 일괄).
- [ ] **2-B-5. 상세페이지 이상 접근** — `?id=존재하지않는키`, `?i=999` 접근 시 폴백 문구 확인(구현돼 있음 — 재확인만).
- [ ] **2-B-6. favicon/터치아이콘** — 운영본 `favicon.png` 이식 또는 신규.

---

## 3. Cutover 설계 — 사전 결정

### 3-A. Vercel 배포 전환 (⭐ §6-Q1 확인 후 확정)
- **확인할 것**: goraesangsa.com이 붙은 Vercel 프로젝트의 ①소유 계정(사용자 본인? 친구?) ②연결 GitHub 레포 ③빌드 설정.
  확인법: Vercel 대시보드 → 프로젝트 → Settings → Domains / Git. 접근 권한이 없으면 친구에게 이양(Transfer) 요청.
- **시나리오 ① (기존 프로젝트에서 연결 레포 교체) — 접근 권한이 있으면 권장, 가장 단순**:
  1. Vercel 프로젝트 Settings → Git → Disconnect → `HotCake0/Test_version` 연결(branch `main`).
  2. Framework Preset = Other(정적), Root Directory = `/`, Build Command 없음, Output = `/`.
  3. 다음 push부터 리워크가 서빙됨. 도메인/DNS/인증서 변경 없음. **롤백 = Vercel Instant Rollback(이전 배포 클릭 1회).**
- **시나리오 ② (새 프로젝트 + 도메인 이전) — 기존 프로젝트를 못 만질 때**:
  1. 본인 Vercel 계정에 `Test_version` import → 임시 `*.vercel.app` URL로 전체 검수(§4-4를 미리 수행 가능. 단 실로그인은 불가).
  2. 기존 프로젝트에서 도메인 제거 → 새 프로젝트에 `goraesangsa.com`+`www.goraesangsa.com` 추가.
  3. DNS는 이미 Vercel을 가리키므로 보통 재검증만으로 붙음(TXT 검증 요구 시 도메인 등록처에서 추가).
  4. 롤백 = 도메인을 옛 프로젝트로 되붙임(수 분).
- 공통: `vercel.json`을 **사전에 레포에 커밋**(§3-B 리다이렉트 포함). apex→www 리다이렉트가 기존과 동일하게
  유지되는지 확인(redirect_uri가 www 고정이므로 www가 정식이어야 함. 확인: `curl -sI https://goraesangsa.com` → www로 30x).

### 3-B. URL 호환 — 리다이렉트 맵 (vercel.json 초안)
- 운영 6페이지 → 리워크 대응 (cleanUrls 유지 — `.html` 접근도 자동 처리됨):

  | 옛 URL | 새 URL | 근거 |
  |---|---|---|
  | `/` | `/` (리워크 index) | — |
  | `/CCTV` | `/pages/multiview` | 멀티뷰 동일 기능 |
  | `/schedule` | `/pages/schedule` | 일정 |
  | `/contest` | `/pages/archive` | 크루대전 기록 |
  | `/ranking` | `/pages/archive` | 통계는 §5-4 재구현 전까지 아카이브로 흡수 |
  | `/admin` | `/pages/admin` | 관리자 |
  | `/auth/callback` | (경로 동일 — 리다이렉트 불필요) | SOOP redirect_uri 불변이 핵심 |

  ```json
  {
    "cleanUrls": true,
    "redirects": [
      { "source": "/CCTV",     "destination": "/pages/multiview", "permanent": true },
      { "source": "/CCTV.html","destination": "/pages/multiview", "permanent": true },
      { "source": "/schedule", "destination": "/pages/schedule",  "permanent": true },
      { "source": "/schedule.html", "destination": "/pages/schedule", "permanent": true },
      { "source": "/contest",  "destination": "/pages/archive",   "permanent": true },
      { "source": "/contest.html",  "destination": "/pages/archive",  "permanent": true },
      { "source": "/ranking",  "destination": "/pages/archive",   "permanent": true },
      { "source": "/ranking.html",  "destination": "/pages/archive",  "permanent": true },
      { "source": "/admin",    "destination": "/pages/admin",     "permanent": false },
      { "source": "/admin.html",    "destination": "/pages/admin",    "permanent": false }
    ]
  }
  ```
  (admin은 `permanent:false` — §3-D 결정에 따라 목적지가 바뀔 수 있음. cleanUrls 환경에선 `.html` source가
  실제 유통 안 될 수 있으나 북마크 대비 포함. 커밋 전 Claude가 Vercel 문서 기준 문법 재검증.)
- 홈 `index.html`의 내부 링크는 이미 `pages/*.html` 상대경로 — cleanUrls가 `.html` 접근을 무확장 URL로
  308 리다이렉트하므로 동작엔 문제 없음. (선택 폴리싱: 빌드에서 링크를 무확장으로 통일 — 후순위.)

### 3-C. 데이터 경로 정책
- **결정: `/rework/*`를 그대로 정식 경로로 사용** (1차 cutover). 근거: 코드·규칙·데이터 무변경 = 리스크 0.
  개명 이전(`/v2/*` 등)은 §5-5 후순위(서비스계정 복사 + `site.js`의 `REWORK_BASE` 1줄 + 규칙 이동이면 되지만 지금 할 이유 없음).
- [ ] **아카이브 재이관**: cutover 직전 운영 `/contests` → `/rework/contests` diff 동기화.
  07-02 이관 후 운영에 추가/수정된 건만 반영(스크립트: 두 컬렉션 fetch → 운영 push키 기준 비교 →
  누락/변경분 admin 토큰 POST/PATCH). Phase A의 "불러오기" 버튼은 목록이 빌 때만 작동하므로 스크립트 필수.
- [ ] **일정 이관**: §2-A-4 매핑대로 (D-Day 단계).
- `/crews`(상대크루 사전)는 그대로 사용(공개 읽기 유지 — 아카이브 상세가 참조).

### 3-D. 운영 전용 기능 인수인계 (⭐ §6-Q4)
| 운영 기능 | 리워크 현황 | 옵션 |
|---|---|---|
| ranking.html — 멤버 참여율/승률 통계, 현역 필터 | 없음 (아카이브에 전적 표시만) | ⓐ §5-4에서 리워크 디자인으로 재구현(권장) ⓑ 포기 |
| admin.html — 기간 반복 일정(groupId 일괄 수정), 멤버 직급색 관리 | admin-*는 데모 목업. 일정 CRUD는 단건만 | ⓐ §5-3에서 기간반복 이식 ⓑ 단건 입력으로 충분하면 포기 |
| image-protect.js — 우클릭/드래그 저장 방지 | 미적용 | ⓐ site.js에 이식(15줄) ⓑ 미적용 |
| 워커 cron 5분 `/status` 갱신 | 리워크 멤버/멀티뷰가 동일 소스 사용 | **그대로 유지(무변경)** |
| update_status.py (수동 갱신 스크립트) | 워커 cron이 대체 중 | 폐기 |

---

## 4. Cutover 실행 런북 (D-Day)

> 예상 소요 1~2시간 + 24시간 집중 관찰. 방송 없는 낮 시간대 권장.
> 사전조건: §1 완료, §2-A-1/2 완료, §3-A/B/D 결정 완료, vercel.json 커밋됨.

- [ ] **4-1. 백업 (T-0h)** — 실행자: Claude + 사용자
  - 코드: 운영 레포에 태그 `prod-final-YYYYMMDD` (또는 로컬 `Whale-Corp-main` zip 보관 — 이미 로컬 사본 있음).
  - 데이터: RTDB 전체 export — Firebase 콘솔 → Realtime Database → 데이터 탭 → ⋮ → "JSON 내보내기"
    (또는 Claude가 admin 토큰으로 `GET /.json` 덤프해 로컬 저장). **합격: 파일 열어 최상위 키 6종 확인.**
- [ ] **4-2. 데이터 최신화** — 실행자: Claude
  - §3-C 아카이브 diff 재이관 → 운영 15건(당시 기준) 대비 rework 건수·필드 일치 검증.
  - §2-A-4 일정 이관 73건(당시 기준) → 건수 일치 + 캘린더 스팟 체크 3건.
- [ ] **4-3. 배포 전환** — 실행자: 사용자(Vercel 콘솔) — §3-A 결정 시나리오 실행.
- [ ] **4-4. 스모크 테스트 (전환 직후 10분)** — 실행자: Claude (curl+Playwright)
  - `https://www.goraesangsa.com/` 및 `pages/*` 19페이지 HTTP 200 + 콘솔 에러 0.
  - 리다이렉트 6종( §3-B 표 ) 30x → 목적지 200.
  - apex→www 리다이렉트 유지. `/auth/callback` 200(코드 없이 접근 시 "인증 코드가 없습니다" 문구 = 정상).
  - `/status` 데이터로 멀티뷰/멤버 LIVE 뱃지 렌더 확인(워커 cron 무영향 증거).
- [ ] **4-5. 실로그인 검증 (사용자 + Claude 안내)** — **Phase B의 첫 실전 검증 지점**
  1. 관리자 계정(울산큰고래 또는 editor 핫케이크_)으로 SOOP 로그인 →
     개발자도구 Application → Session Storage에 `soop_user`(role=admin/editor)와 `soop_fb`(idToken) 생겼는지.
  2. 공지 작성→수정→pinned 토글→삭제 / 클립 작성→featured 토글 / 일정 작성 / 아카이브 수정. 전부 성공해야 함.
  3. 일반 SOOP 계정(권한 미등록)으로 로그인 → 본인 글 작성/수정 성공, 남의 글에 버튼 미노출.
  4. (선택 심화) 일반 계정 콘솔에서 강제 호출:
     `fetch('https://whaie-corp-default-rtdb...app/rework/notices/<남의글키>.json?auth='+JSON.parse(sessionStorage.soop_fb).idToken,{method:'DELETE'})`
     → 401이어야 함(서버 강제의 실증).
  - **실패 시**: 증상별 — `soop_fb` 없음=교환 실패(워커/키 확인), 쓰기 401=토큰 첨부/규칙 확인. Claude 호출해 진단.
- [ ] **4-6. 모니터링** — 첫 24h 집중, 이후 1주.
  - 관찰: 로그인 성공률(멤버 제보), 편집 401 오탐, 멀티뷰 status 5분 갱신, Vercel Analytics 4xx/5xx.
  - **롤백 트리거**: ①로그인 전면 불가 ②주요 페이지 백지/JS 크래시 ③데이터 유실 정황. 사소한 스타일 버그는 전진 수정.
- [ ] **4-7. 롤백 절차** (트리거 발동 시, ~5분)
  - 시나리오①이었으면: Vercel Deployments → 직전(운영본) 배포 → "Instant Rollback".
  - 시나리오②였으면: 도메인을 옛 프로젝트로 재연결.
  - 데이터는 그대로 둬도 안전(운영본은 `/rework`를 안 읽음). 대규모 오염 시에만 4-1 백업 복원.
- [ ] **4-8. 사후 정리 (안정 1주 후)**
  - 개시 공지 게시, 클립/공지 실콘텐츠 입력 마저(§2-A-2·3 — 이제 UI로 가능).
  - 옛 운영 코드 보존 처리(`Whale-Corp-main` → `리워크폐기/` 또는 별도 아카이브), `update_status.py` 폐기.
  - 레포 README 갱신("이 레포가 goraesangsa.com 운영 코드"), 레포명 `Test_version` 개명 검토
    (GitHub 리다이렉트 자동이지만 Vercel Git 연결은 재확인 필요).
  - MEMORY/이 문서 체크박스 갱신.

---

## 5. Cutover 후 백로그 (우선순위순)

### 5-1. Phase C — 운영 데이터 경로 보안 강제 ⭐권장 1순위
현재 `.write:true`인 4경로를 조인다. 전제: cutover 완료(운영본의 무토큰 쓰기가 사라진 뒤).
- **`/status`** — 쓰는 주체가 워커뿐. 워커를 서비스계정 인증으로 전환:
  1. 워커에 Google OAuth2 assertion 플로우 추가 — 이미 있는 WebCrypto 서명 재사용:
     JWT `{iss: SA_EMAIL, scope: "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/firebase.database", aud: "https://oauth2.googleapis.com/token", iat, exp}`
     서명 → `POST https://oauth2.googleapis.com/token` (`grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=...`)
     → access_token(1h, 워커 메모리 캐시) → `PUT /status.json?access_token=...`.
     서비스계정은 **규칙을 우회**(관리자 권한)하므로 규칙은 그냥 `.write:false`로.
  2. 규칙: `"status": { ".read": true, ".write": false }`.
  3. 검증: cron 1주기 후 `/status/updated_at` 갱신 확인 + 무토큰 PUT 401.
- **`/contests` `/schedules` `/crews`(운영 경로)** — cutover 후 아무도 안 씀(리워크는 `/rework` 사용) →
  전부 `".write": false`. 옛 admin.html이 유통 중이면 깨지지만 이미 리다이렉트됨.
- **`/permissions`** — 현행 유지(`.write:false`).
- 배포 물: 워커 재배포 1회 + 규칙 게시 1회. 검증 매트릭스에 status/운영경로 시나리오 추가해 재실행.

### 5-2. RTDB 규칙 정제
- **pinned/featured 관리자 전용 강제** (현재 클라 게이팅만 — owner가 자기 글을 pinned 지정 가능한 구멍):
  ```
  notices/$id/.validate 에 추가:
    (auth.token.admin === true) ||
    (!newData.child('pinned').exists() || newData.child('pinned').val() === (data.child('pinned').exists() ? data.child('pinned').val() : false))
  clips/$id: featured 동일 패턴
  ```
  적용 후 검증: owner가 pinned:true PATCH → 401, admin → 200.
- 필드 스키마 validate: `title.isString() && title.val().length <= 200`, url `newData.val().matches(/^https?:\\/\\//)` 계열.
  (클라 safeUrl의 서버판 — XSS 저장 자체를 차단.)
- ownerNick 위조는 무해(판정은 ownerId)라 보류.

### 5-3. 관리자 페이지 실연동
- admin-clips/notices(-members) 테이블: 데모 alert → `WhaleData` 실 CRUD + 일괄 삭제.
- **기간 반복 일정**(옛 admin.js groupId): 리워크 일정 폼에 "반복(시작일~종료일/요일)" 추가 →
  N건 create에 같은 `groupId` 주입, 수정 시 "연결된 N건 함께 수정" 옵션. §2-A-4에서 groupId 보존해 둔 것과 연결.
- **permissions 관리 UI**: 규칙상 콘솔 전용이므로 워커 경유 필요 —
  `POST /admin/permissions` (idToken 검증→admin claim 확인→서비스계정 access_token으로 쓰기, §5-1 재사용). 중기.

### 5-4. 기능/콘텐츠
- **통계 페이지 재구현**(옛 ranking): `/rework/contests` 기반 참여율/승률/현역필터 — 리워크 디자인. §3-B의 `/ranking` 리다이렉트 목적지 교체.
- LIVE "지금 방송 중" 그리드 섹션 재도입 검토(과거 1회 제거 이력 — 사용자 재요청 시).
- 클립 임베드 플레이어(현재 외부 링크만): SOOP `play.sooplive.com/{id}/embed`·유튜브 iframe, url 타입 감지.
- 멤버 스탯 실데이터(SOOP API 방송시간/팔로워) — 워커 경유 캐시.

### 5-5. 운영 위생
- RTDB 주간 백업 자동화: 워커 cron(주 1회) → `GET /.json`(서비스계정) → GitHub 레포 `backup/` 커밋 또는 R2 저장.
- 서비스계정 키 로테이션 연 1회(절차 = §1-1). 다음 예정: **2027-07**.
- `/rework` → 정식 경로 개명(원하면): 서비스계정 복사 → `site.js REWORK_BASE` 변경 → 규칙 이동 → 구경로 동결.
- Lighthouse 분기 점검(성능/접근성/SEO ≥ 90 목표).

---

## 6. 결정 대기 질문 (사용자 답변 필요)

| # | 질문 | 선택지와 권장 | 막히는 단계 |
|---|---|---|---|
| Q1 | goraesangsa.com Vercel 프로젝트의 소유 계정·연결 레포는? 접근 가능한가? | 접근 가능→시나리오①, 불가→친구에게 이양 요청 or 시나리오② | §3-A, §4-3 |
| Q2 | 일정 시스템: 리워크로 통일(운영 73건 이관) vs 기존 유지? | **①통일 권장**(권한강제 일원화, 이관 스크립트는 Claude 몫) | §2-A-4, §4-2 |
| Q3 | 멤버 16인 최신 직급/부서 확정본? | 운영 조직도+진급 반영해 표로 주시면 반영 | §2-A-1 |
| Q4 | ranking 통계·기간반복 일정·이미지보호 3종 인수 여부? | 통계=재구현 권장, 반복일정=사용빈도 따라, 이미지보호=취향 | §3-D, §5 |
| Q5 | cutover 희망 시기? | §1·§2 완료 후 아무 때나. 방송 없는 낮 권장 | §4 |

---

## 7. 리스크 레지스터

| 리스크 | 확률 | 영향 | 완화/대응 |
|---|---|---|---|
| Vercel 프로젝트 접근 불가(친구 계정) | 중 | cutover 지연 | Q1 조기 확인, 시나리오② 준비됨 |
| cutover 후 실로그인 실패(redirect/CORS 미스매치) | 저 | 편집 불가(열람은 정상) | 경로·www 사전 점검(§3-B), 4-5 즉시 검증, 워커 ALLOWED_ORIGIN 확인 |
| 일정 이관 변환 오류(id→명, 전체태그) | 중 | 캘린더 오표기 | 매핑표 기반 스크립트+건수/스팟 검증, 원본 73건 불변이라 재이관 가능 |
| 옛 URL 유입 깨짐(카톡 공유 링크 등) | 중 | 404 | §3-B 리다이렉트 맵, 배포 직후 6종 실측 |
| 브라우저 캐시로 "안 바뀜" 오인 | 높 | 혼선(실제 장애 아님) | 이 프로젝트 반복 패턴 — Ctrl+Shift+R 먼저, grep/curl로 사실 확인 |
| 규칙 강화 후 예상 밖 401(관리자인데 거부 등) | 저 | 편집 장애 | admin claim은 로그인 시점 발급 — permissions 변경 후엔 재로그인 필요함을 공지 |
| 서비스계정 키 재노출 | 저 | DB 전권 탈취 | §1-1 로테이션, 키는 채팅/레포/OneDrive에 절대 게시 금지, Cloudflare secret에만 |
| OneDrive 동기화 충돌(레포가 OneDrive 안) | 중 | 파일 잠김/유실 | 대량 산출물 생성 금지(기존 사고 교훈), 커밋·푸시로 GitHub가 원본 역할 |

---

## 부록 A. 아키텍처 (현재)

```
[브라우저]
  ├─ 정적: index.html(손수정, site.css 링크) + pages/*.html(산출물 — 수정은 src/build.py!)
  ├─ 공유: assets/site.css(디자인 단일소스), assets/site.js(WhaleUI 게이팅/WhaleData CRUD/idToken 첨부)
  ├─ 로그인: SOOP OAuth(response_type=code) → /auth/callback.html
  │    └ 워커 /auth/token(code→access_token) → /auth/firebase(→커스텀토큰)
  │      → identitytoolkit signInWithCustomToken(→idToken) → sessionStorage.soop_fb
  └─ 쓰기: WhaleData.create/update/remove → RTDB /rework/*.json?auth=idToken

[Cloudflare Worker  whale-status-worker.kyefyx.workers.dev]
  ├─ POST /auth/token · GET /auth/me · POST /auth/firebase · GET /search/bj
  ├─ cron */5: SOOP 라이브 16인 조회 → PUT /status.json  (Phase C에서 서비스계정 인증으로 전환 예정)
  ├─ secrets: SOOP_CLIENT_SECRET, FIREBASE_SA_EMAIL, FIREBASE_SA_KEY   vars: FIREBASE_URL
  └─ 소스: 04_WCHP/whale-auth-worker/worker.js (레포 밖 — 배포는 대시보드 붙여넣기)

[Firebase RTDB  whaie-corp (asia-southeast1)]
  ├─ 운영(공개쓰기, Phase C 대상): /status /contests(15) /schedules(73) /crews
  ├─ /permissions/{닉} = "admin"|"editor"  (.write:false)
  └─ /rework/{notices,clips,schedules,contests} — 서버강제(소유권/admin), 규칙사본 src/firebase-rules.json
```

## 부록 B. 데이터 사전

**`/rework/notices`** (실측): `title, cat(카테고리), date"YYYY-MM-DD", body[문단배열], pinned:bool(관리자),
ownerId, ownerNick, createdAt, updatedAt(ms)`
**`/rework/clips`** (폼 기준): `title, creator, category, date, duration, views:int, img(url|grad), url(https만),
desc, featured:bool(관리자, 단일 유지), owner/시간 4종`
**`/rework/schedules`** (폼: date/time/title/members/type/desc): `date, time"HH:MM", title, members[명],
type(개인방송|합방|대회|특집|공지방송 — TYPE_COLORS 색맵), desc, owner/시간 4종 (+이관분은 groupId 보존)`
**`/rework/contests`** (운영 스키마 그대로): `title, date, games{game_NNN:{name,result:bool(true=승)}},
members[명], opponents[{crewId,name,result:bool ⚠️렌더에서 true=패(반전, 폼이 왕복 보정)}], rank:int,
total_teams:int, notes, videos[{label,type,url}]`
**운영 `/schedules`**: `date, event, members[soop id | "goraesangsa"=전체], groupId?`
**운영 `/contests`**: rework/contests와 동일 스키마(원본)
**`/crews`**: `{pushKey: {aliases[], currentName}}`
**`/status`**: `{members{soopId:{id,name,is_live,title,viewers,thumbnail,live_url}}, updated_at}` — 워커가 5분마다 PUT

## 부록 C. 규칙 검증 매트릭스 (2026-07-07 11/11 PASS — 재실행용 명세)

서비스계정 키로 임의 uid/claim 커스텀토큰 발급 → signInWithCustomToken → REST 호출:
| # | 시나리오 | 기대 |
|---|---|---|
| 1 | 무토큰 POST /rework/notices | 401 |
| 2 | 일반 A: ownerId=A 생성 | 200 |
| 3 | 일반 A: ownerId=B 위조 생성 | 401 |
| 4 | 일반 B: A의 글 PATCH | 401 |
| 5 | 일반 A: 본인 글 PATCH | 200 |
| 6 | 일반 B: A의 글 DELETE | 401 |
| 7 | admin: 남의 글 PATCH | 200 |
| 8 | admin: DELETE | 200 |
| 9 | 일반 A: POST /rework/contests | 401 |
| 10 | admin: contests 생성·삭제 | 200/200 |
| 11 | 무토큰 GET /rework/clips | 200 (읽기 공개) |
스크립트는 세션 휘발(scratchpad `rules-matrix.mjs`) — 필요 시 "검증 매트릭스 다시 돌려줘"로 재작성 요청.
Phase C 이후엔 +3종: 무토큰 PUT /status 401, 무토큰 PUT /contests 401, 워커 cron 후 updated_at 갱신.

## 부록 D. 명령어 치트시트

```bash
# 빌드(18페이지 재생성 — pages/ 직접 수정 금지)
python3 src/build.py
# 로컬 미리보기 (리워크 루트) — 화면 안 바뀌면 Ctrl+Shift+R
python3 -m http.server 8792
# 푸시 (브랜치명 정리 전)
git push origin Test_version:main
# 워커 신규 엔드포인트 생존 확인 (401이면 정상)
curl -s -o /dev/null -w "%{http_code}" -X POST https://whale-status-worker.kyefyx.workers.dev/auth/firebase
# RTDB 컬렉션 건수 훑기
curl -s "https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/rework.json?shallow=true"
```
