# 고래상사 리워크 — 로드맵 v3 (2026-07-08)

> 리워크가 운영(goraesangsa.com)을 대체하는 순간(cutover)까지, 그리고 그 이후의 전체 계획.
> 각 항목에 **실행자 / 선행조건 / 절차 / 합격 기준**을 명시한다. 진행하면서 체크박스를 갱신할 것.
> v3(2026-07-08): 멤버 직급 동기화·아카이브 태그/카테고리·시드 제거·임베드 보안강화 반영 +
> 데이터 사전·검증 명세·이관 경로를 진행분만큼 재구체화. (v2=2026-07-07 실측 구체화, v1=2026-07-07 최초)

---

## 0. 현재 상태 스냅샷

### 0-1. 완료된 것
| 단계 | 내용 | 커밋 |
|---|---|---|
| 18페이지 실구현 | 홈 + crew/members/member, archive(+detail), clips(+clip), schedule(+detail), multiview, notices(+notice), news, admin 5종 | `831d30b` |
| Phase A (07-02) | SOOP 로그인 CRUD 4종(공지·클립·일정·아카이브), `/rework/*` 격리, `WhaleUI`/`WhaleData`, safeUrl XSS 방어 | `63bb07c` |
| Phase B (07-07) | 커스텀토큰 서버 강제 (아래 상세) | `63bb07c` |
| 로드맵 v1·v2 | 이 문서 | `88562ae`·`7d20c3c` |
| **07-08 일괄 (NEW)** | 멤버 직급 동기화 + 아카이브 태그·카테고리 + 시드 제거 + 임베드 보안 + 주석 최신화 | **`1020030`** |

**`1020030`(2026-07-08) 세부** — 전부 빌드·검증 완료(§부록 C-2):
- **멤버 16인 직급/부서/순서 동기화**(§2-A-1 완료): placeholder(영업부·기획실·방송팀 등 가공 부서) → 운영본 조직도(2026-06-08 진급 반영본)의 실제 임원/비서부/게임부/컨텐츠부로 교정. 셀키=인턴(옛 "총무부장" 오류)·멜로딩딩=비서부 부장(옛 "방송팀장" 오류) 등 다수 수정. `rank` 재부여(임원0~/부장10~/사원20~/인턴30~).
- **아카이브↔클립 태그 연결**(§2-A-6 NEW): 클립·아카이브 폼 양쪽에 `tags`(쉼표→배열) 필드. 아카이브 상세가 `D.list('clips')` 후 **태그 교집합(대소문자 무시)** 클립을 "관련 클립" 섹션에 **임베드 미리보기**로 렌더.
- **임베드 미리보기 `embedUrlOf`**(운영 `contest.js getEmbedUrl` 이식 + 보안강화): YouTube·SOOP VOD를 플레이어 임베드로 변환해 **별도 썸네일 이미지 불필요**. ⚠️보안: `new URL` 파싱 + 호스트 엄격검증(정확일치/`.`접미사)으로 iframe src 주입 차단 — `youtube.com/embed/{검증id}`·`*.sooplive.*/player/{숫자}/embed`로만 재조립(원본 패스스루 제거).
- **아카이브 분류(크루대전/컨텐츠)**(§2-A-7 NEW): 폼에 `category` select + 크루전용 필드(순위/상대/게임) 동적 토글. 리스트 필터 칩(전체/🏆크루대전/🎬컨텐츠), 카드·상세 조건부 렌더(컨텐츠는 순위·전적 배지 대신 카테고리 배지). 기존 15건은 category 없음 → **크루대전으로 기본 처리**(하위호환).
- **시드 불러오기 제거**(클립·일정·공지): cutover 전엔 401만 유발 + 실데이터도 아니므로 삭제. 버튼·`importSeed`·죽은 `window.WHALE_*` 주입·`clips_json_script`/`schedule_json_script`/`notices_json_script` 함수까지 정리. **아카이브 운영기록 이관 버튼은 유지**(실데이터 마이그레이션 경로).
- **stale 주석 최신화**: 아카이브 docstring(크루대전→통합), 상세("대회"→"기록"), content JSON `_comment`(clips/schedule/notices — 이제 실 페이지는 Firebase 렌더, 이 JSON은 admin 데모·뉴스 피드 미리보기 전용).
- **뒷정리**: 노출된 서비스계정 키 JSON 삭제(§1-2 완료).

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
- RTDB 규칙 게시(사본 `src/firebase-rules.json`): `/rework` 공개쓰기 제거. **검증 매트릭스 11/11 PASS**(부록 C-1).

### 0-2. 현재 제약 (의도된 상태)
- SOOP OAuth redirect_uri = `https://www.goraesangsa.com/auth/callback` 고정 +
  워커 CORS `ALLOWED_ORIGIN` = `https://www.goraesangsa.com`
  → **리워크 오리진에서는 실로그인 불가 → 편집 기능은 cutover까지 잠김.**
  dev 로그인은 idToken이 없어 쓰기 401(규칙이 막는 게 정상 동작).
  → 이 제약 때문에 시드/이관 버튼이 지금은 무조건 401 (07-08에 클립/일정/공지 시드 제거한 근거).
- 운영 경로(`/status` `/contests` `/schedules` `/crews`)는 여전히 공개쓰기(`.write:true`) —
  운영본이 무토큰으로 쓰는 구조라 cutover 후 Phase C(§5-1)에서 조인다.

### 0-3. 인프라·데이터 실측 (2026-07-07 curl / 2026-07-08 재확인)
- **운영 호스팅 = Vercel** (응답헤더 `server: Vercel`, `vercel.json = {"cleanUrls": true}` 단 1개 설정).
  연결된 Vercel 계정·GitHub 레포는 **미확인**(§6-Q1). 운영 코드 로컬 사본 = `04_WCHP/Whale-Corp-main/`.
- 운영 페이지 6종: `index` `CCTV` `schedule` `ranking` `contest` `admin` (+`auth/callback`).
  운영 조직도(#org, index.html 88~142행)가 **멤버 직급 권위 소스** — cast 슬라이더(146~300행)에 soop id·별명·캐치프레이즈.
- RTDB 현황:
  - `/schedules` **73건 실사용 중** — 스키마 `{date:"YYYY-MM-DD", event:"제목", members:[soop id...], groupId?}`.
    members 고유값 11종 실측: soop id 10종 + `"goraesangsa"`(크루 전체 태그). `groupId`=기간 반복 일정 묶음.
  - `/contests` 15건(운영) / `/rework/contests` 15건(07-02 이관 사본) — cutover 직전 diff 재이관 필요.
    ⚠️이 15건은 `category` 필드 없음 → 리워크 렌더가 크루대전으로 기본 처리(07-08 하위호환). 이관 스크립트에서 `category:"크루대전"` 명시 주입 권장(§3-C).
  - `/rework/notices` 1건 = **dev 테스트 공지**(ownerId `dev:핫케이크_`, title "테스트") → 삭제 대상(§1-4).
  - `/rework/clips`·`/rework/schedules` **비어 있음** (시드 미이관 — 실데이터 넣을 때 충돌 없음).
  - `/crews` = 상대 크루 사전 `{aliases:[], currentName}` (아카이브 상세가 참조). `/permissions` = 닉→"admin"|"editor".
- 이미지 자산(2026-07-08 실측, `img/` 20장 7.5MB): **`wave-bg.png` 4.8MB(최대 압축 대상)**, 멤버 초상 `.png` 200~300KB 다수(멜로딩딩299·삐요코293·채하나284·조아라271·프하200·울산큰고래185). **favicon 없음**. 압축 도구: Pillow 12.2.0 로컬 사용가능, 운영본 `Whale-Corp-main/favicon.png` 이식 가능(§2-B-4/6 참조).
- 레포: `github.com/HotCake0/Test_version`. **로컬 브랜치명 `Test_version`** → 푸시는 `git push origin Test_version:main`.

### 0-4. 리워크 데이터 스키마 (부록 B에 전체 사전)
- 시드 단일소스: `src/content/{members,clips,schedule,notices,site}.json` → `python3 src/build.py` → `pages/*.html`.
  **pages/는 산출물 — 직접 수정 금지, 수정은 build.py/JSON에만.**
- ⚠️07-08 변경: `clips/schedule/notices.json`은 이제 **admin 데모 페이지·뉴스 피드(news) 미리보기 전용 정적 시드**.
  실 clips/schedule/notices 페이지는 Firebase(`WhaleData.list`)에서 렌더하며 이 파일을 안 씀(시드 불러오기·`WHALE_*` 주입 제거됨).
  `members.json`만 여전히 빌드타임 실렌더 소스(crew/members/member + multiview·news의 멤버 메타).
- CRUD 런타임 스키마는 각 폼이 정의(부록 B). 공통 자동 필드: `ownerId, ownerNick, createdAt, updatedAt`.

---

## 1. 즉시 뒷정리 — 보안 (cutover 무관, 지금 바로)

- [~] **1-1. 서비스계정 키 교체** — ⏸ **사용자 보류(2026-07-08 "키는 무시해")**. 아래 절차는 재개 시 참고용으로 보존.
  - 사유: 현행 키(`04cee49a...`)의 private_key가 2026-07-07 채팅에 노출됨. **키 자체는 폐기 전까지 유효**(노출된 채 살아있음).
  - 리스크 수용 판단: 격리된 `/rework`만 영향 + 운영은 무영향이라 사용자가 후순위로 미룸. cutover 전 재개 권장(§5-5 로테이션과 병합 가능).
  - 절차 (⚠️ **이 순서대로 해야 무중단** — 새 키 등록 후 옛 키 삭제):
    1. Firebase 콘솔 → ⚙️ 프로젝트 설정 → 서비스 계정 → "새 비공개 키 생성" → JSON 다운로드.
       (같은 서비스계정 `firebase-adminsdk-fbsvc@whaie-corp.iam.gserviceaccount.com`에 키만 추가됨)
    2. Cloudflare → Workers 및 Pages → whale-status-worker → 설정 → 변수 및 비밀 →
       `FIREBASE_SA_KEY` 편집 → 새 JSON의 `private_key` 값으로 교체(따옴표 안, `\n` 포함 그대로).
       `FIREBASE_SA_EMAIL`은 동일하므로 그대로 둠. **코드 변경·재배포 불필요**(secret 교체만으로 반영).
    3. Google Cloud 콘솔 → 서비스 계정 → firebase-adminsdk 계정 → 키 탭 → 옛 키 `04cee49a...` **삭제**.
    4. 새 JSON 파일도 secret 등록 직후 삭제.
  - 합격 기준(Claude가 실행): ① 가짜 토큰 `POST /auth/firebase` → 400(워커 생존) ② 검증 매트릭스 1·2번 재실행.
- [x] **1-2. 현행 키 JSON 삭제** — ✅ **2026-07-08 완료**(Claude가 `~/Downloads/whaie-corp-firebase-adminsdk-fbsvc-04cee49ab6.json` 삭제). 레포엔 키 값 없음(ROADMAP엔 키 ID·절차만).
- [x] **1-3. (선택) 로컬 브랜치명 정리** — ✅ **2026-07-10 완료**(`Test_version`→`main`, `origin/main` 추적). 이제 `git push`만으로 푸시.
  ```bash
  git branch -m Test_version main
  git fetch origin && git branch -u origin/main main
  git remote set-head origin -a
  ```
- [ ] **1-4. dev 테스트 공지 삭제** — `/rework/notices`의 "테스트" 1건(ownerId `dev:핫케이크_`).
  규칙 강제로 이제 콘솔 외엔 admin 토큰 필요 → Claude가 서비스계정 발급 admin 토큰으로 DELETE
  (검증 매트릭스와 동일 방식), 또는 사용자가 Firebase 콘솔 데이터 탭에서 노드 삭제.
  ⚠️1-1을 "키 무시"로 보류했으므로 서비스계정 토큰 발급도 보류 상태 — cutover 후 admin UI로 삭제하는 게 더 간단할 수 있음.

---

## 2. Cutover 전 준비 — 콘텐츠·품질

### 2-A. 콘텐츠 실데이터화

- [x] **2-A-1. 멤버 직책/부서 확정** — ✅ **2026-07-08 완료**(운영본 조직도에서 추출·반영, 커밋 `1020030`).
  운영 index.html #org를 권위 소스로 사용(사용자 "홈페이지에 정보 있다" 확인). 확정 16인:

  | rank | 이름 | soop id | role | dept |
  |---|---|---|---|---|
  | 0 | 울산큰고래 | bach023 | 사장 | 임원 |
  | 1 | 견자희 | gyeonjahee | 부사장 | 임원 |
  | 10 | 멜로딩딩 | melodingding | 비서부 부장 | 비서부 |
  | 11 | 김마렌 | kimmaren77 | 게임부 부장 | 게임부 |
  | 12 | 감자가비 | doki0818 | 컨텐츠부 부장 | 컨텐츠부 |
  | 20~24 | 이지수·쏭이·조아라·빡쏘·희희덕 | xpdpfv2·gatgdf·joaras2·soyoung6056·poippoi52 | 게임부 사원 | 게임부 |
  | 25~27 | 밀크티냠·삐요코·채하나 | ducke77·nlov555jij·chae1hana | 컨텐츠부 사원 | 컨텐츠부 |
  | 30~31 | 묵아·프하 | nororo·peuhaha | 게임부 인턴 | 게임부 |
  | 32 | 셀키 | sellkey | 컨텐츠부 인턴 | 컨텐츠부 |

  - `stats`(방송시간/클립수/시청자)는 실측 부재로 기존 placeholder 유지 → §5-4(SOOP API 실데이터)에서 교체.
  - 잔여 미세정리(후순위): `crew.html` 프로즈에 "대표이사/신입사원" 옛 표현 잔존, admin-clips 데모 테이블에 옛 부서명(정적 목업이라 무해) — cutover 콘텐츠 손질 때 정리.
- [ ] **2-A-2. 클립 실데이터** — `/rework/clips`가 비어 있음. ⚠️**07-08 시드 불러오기 제거로 경로 변경**:
  - (a) ~~cutover 후 "시드 불러오기" 1클릭~~ **삭제됨**. 대신 필요하면 **Claude가 admin 토큰 이관 스크립트**로 일괄 입력(§3-C 아카이브/일정 이관과 동일 패턴, `clips.json`→`/rework/clips` POST).
  - (b) **cutover 후 관리자 로그인으로 UI에서 직접 입력**(권장 — 실데이터가 적고 사용자가 직접 골라 넣는 게 자연스러움).
  - 입력 팁: `url`은 `https?://`만 통과(safeUrl). SOOP VOD = `https://vod.sooplive.com/player/{id}`, 유튜브 = `youtu.be/{id}` 또는 `watch?v={id}`. **이미지 URL은 선택** — 비우면 카드/관련클립이 영상 링크로 임베드 미리보기(07-08 embedUrlOf), SOOP 썸네일 이미지를 따로 구할 필요 없음. `tags`에 관련 아카이브 태그 넣으면 그 아카이브 상세에 자동 노출.
- [ ] **2-A-3. 공지 실데이터** — §1-4 테스트 공지 삭제 후, 개시 공지(리뉴얼 안내 등) 준비.
  ⚠️07-08 공지 시드 제거 → cutover 후 admin UI 입력이 정석(급하면 Claude admin 토큰 대행). news 피드 미리보기는 `notices.json` 정적 시드를 계속 씀(실 공지와 별개).
- [~] **2-A-4. 일정 데이터 통합** — ❌**2026-07-10 이관 취소(사용자 결정)**: 운영 `/schedules` 73건이 **전부 과거(2026-05-01~06-23)**라 이관 무의미. 리워크 캘린더는 cutover 후 관리자 UI로 **예정 일정부터 신규 입력**. 아래 매핑표는 향후 필요 시 참고용 보존.
  - 스키마 매핑 (운영 `/schedules` 73건 → `/rework/schedules`):

    | 운영 필드 | 리워크 필드 | 변환 |
    |---|---|---|
    | `date` "YYYY-MM-DD" | `date` | 그대로 |
    | `event` | `title` | 그대로 |
    | `members` [soop id] | `members` [멤버명] | 워커 `CREW_MEMBERS` 맵(id→명)으로 변환. **이제 `members.json`의 확정 16인 매핑(§2-A-1)과 교차검증 가능**. `"goraesangsa"` → 16인 전원 또는 `["고래상사 전체"]` 태그(리워크 렌더 확인 후 결정) |
    | `groupId` | (보존) | 리워크 폼엔 없지만 보존(§5-3 기간반복 대비) |
    | (없음) | `time` | `""` (미상) |
    | (없음) | `type` | members 1인=개인방송, 2인 이상=합방, 전체태그=특집 등 규칙 매핑(스크립트) |
    | (없음) | `desc` | `""` |
    | (없음) | `ownerId/ownerNick/createdAt/updatedAt` | 서비스계정 이관 시 admin 소유로 주입(`ownerId`=관리자 soop id `bach023` 권장) |
  - 실행: Claude가 이관 스크립트 작성(admin 토큰 POST) → 건수 73=73 검증 → 리워크 캘린더 렌더 확인.
  - 이관 후 운영 admin.js 일정 시스템은 읽기 전용 유산이 됨(§3-D에서 인수 결정).
  - 시점: **cutover 직전**(그 사이 운영에 새 일정이 계속 추가되므로 D-Day 단계에 포함, §4-2).
- [ ] **2-A-5. 뉴스 피드** — news.html은 공지+클립+일정 통합 피드. ⚠️**현재 정적 시드(`NOTICES/CLIPS/SCHEDULE` 상수)로 렌더** — Firebase 실데이터와 별개(빌드타임 미리보기). cutover 후 실데이터 반영하려면 news도 `WhaleData.list` 런타임 로드로 전환 필요(§5-4 소규모 항목으로 이동). 지금은 확인만.
- [x] **2-A-6. 아카이브↔클립 태그 연결** — ✅ **2026-07-08 완료**(`1020030`).
  - 클립·아카이브 폼에 `tags`(쉼표→배열). 아카이브 상세 하단 "관련 클립": `D.list('clips')` 후 태그 교집합(소문자 정규화) 필터 → 카드 그리드에 임베드(YouTube/SOOP) 또는 정적 썸네일 폴백.
  - 임베드 helper `embedUrlOf`(build_archive_detail 인라인): `new URL` 파싱→호스트 화이트리스트(`youtu.be`/`youtube(-nocookie).com`/`sooplive.com`/`sooplive.co.kr`, 정확일치·`.`접미사) → 검증된 id/숫자로만 재조립. **저장형 iframe-src 주입 차단**(보안리뷰 지적 반영, 부록 C-2 10/10 PASS).
  - 운영 방법(사용자): 아카이브 기록과 클립에 같은 태그(예 "여름특집")를 넣으면 그 기록 상세에 해당 클립들이 미리보기로 뜸.
- [x] **2-A-7. 아카이브 카테고리(크루대전/컨텐츠)** — ✅ **2026-07-08 완료**(`1020030`).
  - `category` select(크루대전|컨텐츠), 폼에서 컨텐츠 선택 시 순위/상대/게임 필드 자동 숨김. 리스트 칩(전체/🏆크루대전/🎬컨텐츠) 클라 필터. 카드·상세: 크루대전=순위/전적, 컨텐츠=카테고리 배지만.
  - 기존 15건(category 없음)=크루대전 기본. 헤더 "통합 아카이브", 상세 "기록 상세"로 문구 일반화.
  - 남은 것: 컨텐츠 카테고리 **실데이터 입력**(cutover 후 admin UI, 또는 Claude 대행). 컨텐츠 항목은 순위/상대/게임 비우고 제목·날짜·멤버·영상·태그만.

### 2-B. 품질 점검

- [x] **2-B-1. 모바일/반응형** — ✅**2026-07-10 에뮬레이션 점검 통과**(Playwright 390px isMobile, 12페이지). **가로 스크롤바 0**, 칩 줄바꿈·캘린더 7열·멤버 단일컬럼·히어로 다 정상(스크린샷 확인). 유일 노트: index만 레이아웃뷰포트 466px(멤버 Swiper 캐러셀 초기화 전 슬라이드 폭 탓, **시각적 깨짐 없음·경미**) — 취약한 손수정 메인이라 미수정, 실기기 최종확인 권장. 실행자: 사용자(메모리 방침: UI 확인은 사용자).
  중점: 홈 sec02 가로핀 모바일 폴백(≤860px 세로 스택), 하위페이지 드로어, CRUD 모달 폼 입력(모바일 키보드),
  캘린더 7열 그리드 축소, 멀티뷰 iframe 그리드, **NEW: 아카이브 카테고리 칩 줄바꿈·관련클립 임베드 그리드(≥210px 오토필)**.
- [x] **2-B-2. reduced-motion + 콘솔 에러 0** — ✅**2026-07-10 순회 통과**(18페이지 ×2모드). **우리 코드 콘솔에러 0**. 잡힌 2건은 전부 외부/환경: ①member 상세 "auto play block"=SOOP `LivePlayer.js`가 헤드리스 autoplay 차단에 던진 것(실브라우저 정상) ②multiview `ERR_CERT_DATE_INVALID`=`liveimg.afreecatv.com` 썸네일, WSL 시계오차로 TLS 검증 실패(환경 아티팩트). reduced-motion 양쪽 동일.
  - ⚙️**sudo 없이 Chromium 실행법**(재현용): WSL Ubuntu 26.04엔 libnspr4/nss3/asound 누락 → `apt-get download libnspr4 libnss3 libasound2t64`(무sudo) → `dpkg-deb -x`로 로컬 추출 → `LD_LIBRARY_PATH=<prefix>/usr/lib/x86_64-linux-gnu node sweep.mjs`. 스크립트=scratchpad `sweep.mjs`/`responsive.mjs`.
  19페이지 순회: HTTP 200, console error 0, `prefers-reduced-motion` 에뮬레이션 시 인트로/핀 비활성 확인.
  **NEW 주의: 아카이브 상세 관련클립 임베드 iframe이 콘솔 에러(third-party 쿠키 경고 등) 유발 가능 — 실오류와 구분.**
- [x] **2-B-3. SEO/메타 일괄** ✅**2026-07-10**(favicon·description·og·twitter, canonical만 §3-B로 보류) — 실행자: Claude. build.py `head()`(build.py 49행)에 페이지별
  `<meta name="description">`, `og:title/description/image`(대표 이미지 1장 지정 — 후보: 운영 `favicon.png` 또는 홈 히어로), `<link rel="canonical">`.
  홈 index.html은 손수정(검증본 인라인 유지 — head만 추가). 합격: 전 페이지 meta 존재 + 카톡 공유 미리보기 정상.
- [x] **2-B-4. 이미지 최적화** ✅**2026-07-10 완료**(img/ 7.5MB→1.6MB, wave-bg 삭제+초상 재압축, `2eb5a0d`) — 실행자: Claude(Pillow 12.2.0). **실측 기반 구체화**:
  - 최우선 `img/wave-bg.png` **4.8MB** → 배경용이라 리사이즈+재압축(예: 폭 1920 축소 + PNG 최적화/WebP, 목표 <300KB).
  - 200KB 초과 초상 6장(멜로딩딩·삐요코·채하나·조아라·프하·울산큰고래) → 품질 유지 재압축 목표 <150KB.
  - `loading="lazy"` 빌드 템플릿 일괄 부여(멤버/클립/관련클립 img). 합격: `img/` 총량 7.5MB→<2MB, 육안 화질 저하 없음.
- [x] **2-B-5. 상세페이지 이상 접근** ✅**2026-07-10 재확인**(5개 상세 모두 폴백 문구 존재) — `?id=존재하지않는키`, `?i=999` 접근 시 폴백 문구 확인(구현돼 있음 — 재확인만).
  아카이브 상세: 없는 id → "기록을 찾을 수 없습니다" + 목록 링크(07-08 문구 확인).
- [x] **2-B-6. favicon/터치아이콘** ✅**2026-07-10**(운영본 favicon.png 루트 이식, 전 페이지 icon+apple-touch) — 운영본 `Whale-Corp-main/favicon.png` 이식(build.py `head()`에 `<link rel="icon">` + apple-touch-icon). 현재 리워크에 favicon 전무.

---

## 2.5. 담금질 기간 (2026-07-10 ~ 08-03 D-Day) — Q5 확정으로 신설

필수 선행조건은 §1~§3에서 전부 소진 — 이 구간은 **완성도 상향 전용**(사용자 방침: "완성도를 계속 높이고 다듬고 담금질"). 후보 백로그(우선순위 제안, 진행하며 갱신):

- [ ] **2.5-1. impeccable 재-critique** — 07-08 채점 25/40 이후 P0/P1/P2·AI티 정리를 전부 반영했으므로 재채점으로 남은 감점 요인 식별 → 후속 수정. 담금질 기간의 나침반 역할.
- [ ] **2.5-2. ranking 통계 재구현 앞당김** — Q4에서 §5-4(cutover 후)로 결정했으나 3주 여유가 생겨 **앞당김 가능**. 운영 ranking.js 로직(참여율/승률/현역 필터) + 리워크 디자인. 완성되면 §3-B `/ranking` 리다이렉트 목적지를 신설 페이지로 교체.
- [x] **2.5-3. news 피드 런타임 전환** ✅**2026-07-11 완료** — build_news()를 `D.list('notices'|'clips'|'schedules')` 런타임 렌더로 교체. 히어로=고정공지 우선(없으면 최신), 클립=createdAt 최신 5, 일정=오늘 이후 5. 패널별 빈 문구·실패 문구, `.news-empty` 스타일. 시드 상수는 news에서 미사용(다른 페이지 미리보기는 유지). node --check 통과.
- [ ] **2.5-4. 콘텐츠 사전 준비** — 개시 공지 문구 초안, 클립 후보 목록(URL+태그) 선정. 입력 자체는 cutover 후 admin UI지만 준비는 미리(사용자 주도, Claude 보조).
- [x] **2.5-5. 미세정리 일괄** ✅**2026-07-11** — crew 프로즈 "사장부터 인턴까지·비서/게임/컨텐츠"로 교정(build.py+재빌드). admin-* 옛 부서명은 조사 결과 이미 없음. index 466px는 취약한 손수정 메인이라 **의도적 미수정 유지**(2-B-1 결론 준용, 시각적 깨짐 없음).
- [ ] **2.5-6. D-Day 리허설** — 본인 Vercel 계정에 `Test_version` 별도 import → 임시 `*.vercel.app`에서 vercel.json 리다이렉트·cleanUrls·전 페이지 실배포 검수(§4-4 사전 수행, 실로그인만 제외). 리허설 후 프로젝트 삭제.
- [ ] **2.5-7. 실기기 모바일 최종 확인**(사용자) — 2-B-1 에뮬레이션 통과분의 실기기 재확인.
- ⏸ (보류 유지) §1-1 키 교체 — 사용자 결정. D-Day 전 재개 권장 입장만 보존.

---

## 3. Cutover 설계 — 사전 결정

### 3-A. Vercel 배포 전환 (✅ §6-Q1 확정 — 사용자 본인 계정, 시나리오① 적용)
- **확정(2026-07-10)**: goraesangsa.com Vercel 프로젝트 = **사용자 본인 계정**. → 계정 이양·도메인 이전 불필요, **시나리오①**로 진행. 남은 확인은 연결 레포·빌드 설정뿐(cutover 때).
- **시나리오 ① (기존 프로젝트에서 연결 레포 교체) — ✅채택, 가장 단순**:
  1. Vercel 프로젝트 Settings → Git → Disconnect → `HotCake0/Test_version` 연결(branch `main`).
  2. Framework Preset = Other(정적), Root Directory = `/`, Build Command 없음, Output = `/`.
  3. 다음 push부터 리워크가 서빙됨. 도메인/DNS/인증서 변경 없음. **롤백 = Vercel Instant Rollback(이전 배포 클릭 1회).**
- **시나리오 ② (새 프로젝트 + 도메인 이전) — 기존 프로젝트를 못 만질 때**:
  1. 본인 Vercel 계정에 `Test_version` import → 임시 `*.vercel.app`로 전체 검수(§4-4 사전수행 가능, 단 실로그인 불가).
  2. 기존 프로젝트에서 도메인 제거 → 새 프로젝트에 `goraesangsa.com`+`www.goraesangsa.com` 추가.
  3. DNS는 이미 Vercel을 가리키므로 보통 재검증만으로 붙음(TXT 요구 시 등록처에서 추가).
  4. 롤백 = 도메인을 옛 프로젝트로 되붙임(수 분).
- 공통: `vercel.json`을 **사전에 레포에 커밋**(§3-B 리다이렉트 포함 — ✅2026-07-10 완료). apex→www 리다이렉트 유지 확인
  (redirect_uri가 www 고정이므로 www가 정식. `curl -sI https://goraesangsa.com` → www로 30x).

### 3-B. URL 호환 — 리다이렉트 맵 (✅ 2026-07-10 `vercel.json` 레포 루트 커밋 완료 — Vercel 문서로 문법 재검증(permanent true=308·cleanUrls .html 자동 308), 대상 10건 존재 확인, `$schema` 추가. 남은 것: cutover 때 admin 목적지 §3-D 재확인만)
- 운영 6페이지 → 리워크 대응 (cleanUrls 유지 — `.html` 접근도 자동 처리):

  | 옛 URL | 새 URL | 근거 |
  |---|---|---|
  | `/` | `/` (리워크 index) | — |
  | `/CCTV` | `/pages/multiview` | 멀티뷰 동일 기능 |
  | `/schedule` | `/pages/schedule` | 일정 |
  | `/contest` | `/pages/archive` | 아카이브(크루대전 기본 필터로 착지) |
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
  (admin은 `permanent:false` — §3-D 결정에 따라 목적지 변동 가능. 커밋 전 Claude가 Vercel 문서 기준 문법 재검증.)
- 홈 `index.html`의 내부 링크는 이미 `pages/*.html` 상대경로 — cleanUrls가 무확장 URL로 308. (선택 폴리싱: 링크 무확장 통일 — 후순위.)

### 3-C. 데이터 경로 정책
- **결정: `/rework/*`를 그대로 정식 경로로 사용** (1차 cutover). 근거: 코드·규칙·데이터 무변경 = 리스크 0.
  개명 이전(`/v2/*` 등)은 §5-5 후순위(서비스계정 복사 + `site.js REWORK_BASE` 1줄 + 규칙 이동).
- [ ] **아카이브 재이관**: cutover 직전 운영 `/contests` → `/rework/contests` diff 동기화.
  07-02 이관 후 운영 추가/수정분만 반영(스크립트: 두 컬렉션 fetch → push키 비교 → 누락/변경분 admin POST/PATCH).
  ⚠️07-08 이후 이관 스크립트는 각 건에 **`category:"크루대전"` 명시 주입**(하위호환 넘어 데이터 정합). "불러오기" 버튼은 목록 빌 때만 작동하므로 diff엔 스크립트 필수.
- [ ] **일정 이관**: §2-A-4 매핑대로 (D-Day 단계).
- `/crews`(상대크루 사전)는 그대로 사용(공개 읽기 유지 — 아카이브 상세가 참조).

### 3-D. 운영 전용 기능 인수인계 (✅ §6-Q4 확정 — 2026-07-10 사용자 "권장으로 진행")
| 운영 기능 | 리워크 현황 | 결정 |
|---|---|---|
| ranking.html — 멤버 참여율/승률 통계, 현역 필터 | 없음(아카이브에 전적 표시만) | **ⓐ 채택**: §5-4에서 리워크 디자인 재구현(cutover 후). 공백 기간엔 `/ranking`→archive 리다이렉트가 커버 |
| admin.html — 기간 반복 일정(groupId 일괄), 멤버 직급색 관리 | admin-*는 데모 목업. 일정 CRUD 단건만 | **ⓑ 채택**: 단건 유지·포기. 반복 입력 실수요 확인되면 §5-3 재검토 |
| image-protect.js — 우클릭/드래그 저장 방지 | ✅**ⓐ 이식 완료(2026-07-10)** | site.js IIFE 끝부분 + index.html 인라인(홈은 site.js 미로드) 두 곳. IMG 한정 contextmenu/dragstart 차단 |
| 워커 cron 5분 `/status` 갱신 | 리워크 멤버/멀티뷰가 동일 소스 사용 | **그대로 유지(무변경)** |
| update_status.py (수동 갱신) | 워커 cron이 대체 | 폐기 |

---

## 4. Cutover 실행 런북 (D-Day = **2026-08-03 확정**, 방송 없는 낮 시간대)

> 예상 소요 1~2시간 + 24시간 집중 관찰. 방송 없는 낮 시간대 권장.
> 사전조건: §1-4 완료(테스트공지 삭제), §2-A-2/3(클립·공지 준비), §3-A/B/D 결정, vercel.json 커밋. (§1-1 키교체는 사용자 보류 상태 — cutover 전 재개 권장하나 blocker 아님.)

- [ ] **4-1. 백업 (T-0h)** — Claude + 사용자
  - 코드: 운영 레포에 태그 `prod-final-YYYYMMDD` (또는 로컬 `Whale-Corp-main` zip — 이미 로컬 사본 있음).
  - 데이터: RTDB 전체 export — Firebase 콘솔 → RTDB → 데이터 탭 → ⋮ → "JSON 내보내기"
    (또는 Claude가 `GET /.json` 덤프). **합격: 파일 열어 최상위 키 6종 확인.**
- [ ] **4-2. 데이터 최신화** — Claude
  - §3-C 아카이브 diff 재이관(+`category` 주입) → 건수·필드 일치 검증.
  - §2-A-4 일정 이관 73건(당시 기준) → 건수 일치 + 캘린더 스팟 체크 3건.
- [ ] **4-3. 배포 전환** — 사용자(Vercel 콘솔) — §3-A 결정 시나리오 실행.
- [ ] **4-4. 스모크 테스트 (전환 직후 10분)** — Claude(curl+Playwright)
  - `https://www.goraesangsa.com/` 및 `pages/*` 19페이지 HTTP 200 + 콘솔 에러 0.
  - 리다이렉트 6종(§3-B) 30x → 목적지 200. apex→www 유지. `/auth/callback` 200(코드 없이=문구 정상).
  - `/status` 데이터로 멀티뷰/멤버 LIVE 뱃지 렌더(워커 cron 무영향 증거).
  - **NEW: 아카이브 카테고리 칩 필터 동작 + 관련클립 임베드 렌더 스팟 체크.**
- [ ] **4-5. 실로그인 검증 (사용자 + Claude 안내)** — **Phase B의 첫 실전 검증 지점**
  1. 관리자(울산큰고래 or editor 핫케이크_) SOOP 로그인 → Session Storage `soop_user`(role) + `soop_fb`(idToken) 확인.
  2. 공지 작성→수정→pinned 토글→삭제 / 클립 작성→featured 토글→**태그 넣고 관련아카이브 노출 확인** / 일정 작성 / 아카이브 수정→**카테고리 전환 확인**. 전부 성공.
  3. 일반 SOOP 계정(권한 미등록) 로그인 → 본인 글 작성/수정 성공, 남의 글 버튼 미노출.
  4. (심화) 일반 계정 콘솔 강제 호출: `fetch('.../rework/notices/<남의글키>.json?auth='+idToken,{method:'DELETE'})` → 401.
  - **실패 시**: `soop_fb` 없음=교환 실패(워커/키), 쓰기 401=토큰첨부/규칙. Claude 호출 진단.
- [ ] **4-6. 모니터링** — 첫 24h 집중, 이후 1주. 로그인 성공률·편집 401 오탐·멀티뷰 5분갱신·Vercel 4xx/5xx.
  - **롤백 트리거**: ①로그인 전면불가 ②주요페이지 백지/크래시 ③데이터 유실. 사소한 스타일은 전진 수정.
- [ ] **4-7. 롤백** (~5분): 시나리오①=Vercel Instant Rollback / ②=도메인 재연결. 데이터는 둬도 안전(운영본은 `/rework` 안 읽음).
- [ ] **4-8. 사후 정리 (안정 1주 후)**
  - 개시 공지 게시, 클립/공지/컨텐츠 아카이브 실콘텐츠 입력(§2-A-2·3·7 — UI로 가능).
  - 옛 운영 코드 보존(`Whale-Corp-main` → `리워크폐기/`), `update_status.py` 폐기.
  - 레포 README 갱신, 레포명 `Test_version` 개명 검토(Vercel Git 재확인 필요).
  - §1-1 키 로테이션 재개 검토. MEMORY/이 문서 체크박스 갱신.

---

## 5. Cutover 후 백로그 (우선순위순)

### 5-1. Phase C — 운영 데이터 경로 보안 강제 ⭐권장 1순위
현재 `.write:true`인 4경로를 조인다. 전제: cutover 완료(운영본 무토큰 쓰기 소멸 후).
- **`/status`** — 쓰는 주체가 워커뿐. 워커를 서비스계정 인증으로 전환:
  1. 워커에 Google OAuth2 assertion 추가(기존 WebCrypto 서명 재사용):
     JWT `{iss:SA_EMAIL, scope:"...userinfo.email ...firebase.database", aud:"https://oauth2.googleapis.com/token", iat, exp}`
     → `POST oauth2.googleapis.com/token`(`grant_type=...jwt-bearer&assertion=...`) → access_token(1h 캐시) → `PUT /status.json?access_token=...`.
     서비스계정은 규칙 우회(관리자) → 규칙은 `.write:false`.
  2. 규칙: `"status": { ".read": true, ".write": false }`.
  3. 검증: cron 1주기 후 `/status/updated_at` 갱신 + 무토큰 PUT 401.
- **`/contests` `/schedules` `/crews`(운영 경로)** — cutover 후 아무도 안 씀 → 전부 `".write": false`.
- **`/permissions`** — 현행 유지(`.write:false`).
- 배포: 워커 재배포 1회 + 규칙 게시 1회. 검증 매트릭스에 status/운영경로 시나리오 추가(부록 C-1 +3종).

### 5-2. RTDB 규칙 정제
- **pinned/featured 관리자 전용 강제** (현재 클라 게이팅만 — owner가 자기 글 pinned 지정 가능한 구멍):
  ```
  notices/$id/.validate 추가:
    (auth.token.admin === true) ||
    (!newData.child('pinned').exists() || newData.child('pinned').val() === (data.child('pinned').exists() ? data.child('pinned').val() : false))
  clips/$id: featured 동일 패턴
  ```
  적용 후 검증: owner pinned:true PATCH → 401, admin → 200.
- 필드 스키마 validate: `title.isString() && length<=200`, url `matches(/^https?:\/\//)` 계열(클라 safeUrl의 서버판).
  **NEW: `tags`도 검증 대상 — 문자열/배열 타입·개수 상한(예 ≤10). 임베드는 클라 embedUrlOf가 이미 호스트 강제하나, 저장 자체를 조일 거면 url validate와 함께.**
- ownerNick 위조는 무해(판정은 ownerId)라 보류.

### 5-3. 관리자 페이지 실연동
- admin-clips/notices(-members) 테이블: 데모 alert → `WhaleData` 실 CRUD + 일괄 삭제. (07-08 시점 여전히 정적 목업.)
- **기간 반복 일정**(옛 admin.js groupId): 리워크 일정 폼에 "반복(시작~종료/요일)" → N건 create에 같은 `groupId`, 수정 시 "연결 N건 함께" 옵션. §2-A-4에서 groupId 보존해 둔 것과 연결.
- **permissions 관리 UI**: 콘솔 전용이므로 워커 경유 — `POST /admin/permissions`(idToken→admin claim→서비스계정 access_token 쓰기, §5-1 재사용). 중기.

### 5-4. 기능/콘텐츠
- **통계 페이지 재구현**(옛 ranking): `/rework/contests` 기반 참여율/승률/현역필터 — 리워크 디자인. §3-B `/ranking` 목적지 교체.
- **news 실데이터 전환**: 현재 정적 시드 렌더 → `WhaleData.list`(notices+clips+schedules) 런타임 통합 피드로. (소규모, §2-A-5에서 이관.)
- **클립 임베드 플레이어 확대**: 07-08 아카이브 관련클립엔 임베드 적용됨. 클립 페이지/상세 본체에도 `embedUrlOf` 재사용해 인라인 재생 도입(현재 외부 링크). embedUrlOf를 공유 헬퍼(site.js)로 승격 검토.
- **멤버 스탯 실데이터**(SOOP API 방송시간/팔로워) — 워커 경유 캐시 → `members.json` stats placeholder 교체(§2-A-1 연계).
- LIVE "지금 방송 중" 그리드 재도입 검토(과거 제거 이력 — 재요청 시).

### 5-5. 운영 위생
- RTDB 주간 백업 자동화: 워커 cron(주1회) → `GET /.json`(서비스계정) → GitHub `backup/` 커밋 또는 R2.
- 서비스계정 키 로테이션(절차 §1-1). **§1-1이 보류 중이므로 cutover 전 1회는 반드시 수행 권장**. 이후 연1회(다음 2027-07).
- `/rework` → 정식 경로 개명(원하면): 서비스계정 복사 → `site.js REWORK_BASE` → 규칙 이동 → 구경로 동결.
- Lighthouse 분기 점검(성능/접근성/SEO ≥ 90). 2-B-4 이미지 최적화 후 재측정.

---

## 6. 결정 대기 질문 (사용자 답변 필요)

| # | 질문 | 선택지와 권장 | 막히는 단계 | 상태 |
|---|---|---|---|---|
| Q1 | goraesangsa.com Vercel 프로젝트 소유 계정·연결 레포? 접근 가능? | ~~접근 가능→시나리오①~~ **✅해결(2026-07-10 본인 계정 확인 → 시나리오① 확정)** | §3-A,§4-3 | ✅완료 |
| Q2 | 일정: 리워크 통일(73건 이관) vs 기존 유지? | ~~①통일 권장~~ **✅해결(2026-07-10): 이관 취소 — 운영 73건 전부 과거라 무의미. cutover 후 신규 입력** | §2-A-4 | ✅완료 |
| Q3 | 멤버 16인 최신 직급/부서? | ~~표로 주시면 반영~~ **✅해결(운영 조직도에서 추출, 2-A-1 완료)** | §2-A-1 | ✅완료 |
| Q4 | ranking 통계·기간반복·이미지보호 인수 여부? | **✅해결(2026-07-10 "권장으로 진행"): 통계=§5-4 백로그 재구현, 기간반복=포기(수요 확인 시 §5-3 재검토), 이미지보호=이식 완료(site.js+index.html)** | §3-D,§5 | ✅완료 |
| Q5 | cutover 희망 시기? | **✅확정(2026-07-10): D-Day = 2026-08-03.** 그때까지 완성도 담금질 기간(§2.5) — 방송 없는 낮 시간대에 §4 런북 실행 | §4 | ✅완료 |
| Q6 | 서비스계정 키(§1-1) 교체 재개 시점? | 07-08 "무시"·**07-10 재보류(사용자 "키는 제외")** → cutover 전 1회 권장 유지(§5-5) | §1-1 | 보류 |

---

## 7. 리스크 레지스터

| 리스크 | 확률 | 영향 | 완화/대응 |
|---|---|---|---|
| ~~Vercel 프로젝트 접근 불가(친구 계정)~~ | — | — | ✅해소(2026-07-10 본인 계정 확인, 시나리오①) |
| cutover 후 실로그인 실패(redirect/CORS) | 저 | 편집 불가(열람 정상) | 경로·www 사전 점검(§3-B), 4-5 즉시 검증, 워커 ALLOWED_ORIGIN 확인 |
| 일정 이관 변환 오류(id→명, 전체태그) | 중 | 캘린더 오표기 | 매핑표+§2-A-1 확정 16인 교차검증, 건수/스팟 검증, 원본 불변이라 재이관 가능 |
| 아카이브 이관 시 category 누락 | 중 | 필터에 안 잡힘 | §3-C 스크립트에서 `category` 명시 주입 + 렌더 기본값(크루대전) 이중안전 |
| 클립/컨텐츠 태그 오타로 관련클립 미매칭 | 중 | 연결 누락(장애 아님) | 소문자 정규화 매칭, 입력 시 기존 태그 재사용 권장. §5-3에서 태그 자동완성 검토 |
| 악의적 클립 url로 iframe 주입 시도 | 저 | (차단됨) | 07-08 embedUrlOf 호스트강제로 차단(부록 C-2). §5-2 서버 url validate로 저장차단 추가 가능 |
| 옛 URL 유입 깨짐(카톡 공유) | 중 | 404 | §3-B 리다이렉트 맵, 배포 직후 6종 실측 |
| 브라우저 캐시 "안 바뀜" 오인 | 높 | 혼선(장애 아님) | 반복 패턴 — Ctrl+Shift+R 먼저, grep/curl로 사실 확인 |
| 규칙 강화 후 예상 밖 401(관리자인데 거부) | 저 | 편집 장애 | admin claim은 로그인 시점 발급 — permissions 변경 후 재로그인 필요 공지 |
| 서비스계정 키 재노출/현행 노출키 방치 | 중 | DB 전권 탈취 | §1-1(현재 보류) cutover 전 로테이션, 키는 채팅/레포/OneDrive 절대 금지, Cloudflare secret에만 |
| OneDrive 동기화 충돌(레포가 OneDrive 안) | 중 | 파일 잠김/유실 | 대량 산출물 금지, 커밋·푸시로 GitHub가 원본 |

---

## 부록 A. 아키텍처 (현재)

```
[브라우저]
  ├─ 정적: index.html(손수정, site.css 링크) + pages/*.html(산출물 — 수정은 src/build.py!)
  ├─ 공유: assets/site.css(디자인 단일소스), assets/site.js(WhaleUI 게이팅/WhaleData CRUD/idToken 첨부)
  ├─ 로그인: SOOP OAuth(response_type=code) → /auth/callback.html
  │    └ 워커 /auth/token(code→access_token) → /auth/firebase(→커스텀토큰)
  │      → identitytoolkit signInWithCustomToken(→idToken) → sessionStorage.soop_fb
  ├─ 쓰기: WhaleData.create/update/remove → RTDB /rework/*.json?auth=idToken
  └─ 아카이브 상세: D.list('contests')+D.list('clips') → 태그 교집합 "관련 클립"
       → embedUrlOf(호스트강제)로 YouTube/SOOP 임베드 iframe (07-08)

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

**`src/content/members.json`** (빌드타임 실렌더 소스, 16인): `slug, name, role(직책), dept(임원|비서부|게임부|컨텐츠부),
rank(정렬키 임원0~/부장10~/사원20~/인턴30~), color(그라데이션), initials, img(리워크루트 상대), bio, stats[{n,u}]×3, soop(id)`.
직급/부서/순서 권위 소스 = 운영 index.html #org (07-08 동기화, §2-A-1 표).
**`/rework/notices`** (실측): `title, cat(카테고리), date"YYYY-MM-DD", body[문단배열], pinned:bool(관리자), owner/시간 4종`
**`/rework/clips`** (폼 기준, 07-08 `tags` 추가): `title, creator, category, desc, url(https만), img(url|비우면 임베드/그라데이션),
tags[문자열](아카이브 연결키), featured:bool(관리자, 단일 유지), owner/시간 4종`
**`/rework/schedules`** (폼: date/time/title/members/type/desc): `date, time"HH:MM", title, members[명],
type(개인방송|합방|대회|특집|공지방송 — TYPE_COLORS 색맵), desc, owner/시간 4종 (+이관분 groupId 보존)`
**`/rework/contests`** (07-08 `category`·`tags` 추가): `category(크루대전|컨텐츠, 없으면 크루대전), title, date,
games{game_NNN:{name,result:bool(true=승)}}, members[명], opponents[{crewId,name,result:bool ⚠️렌더 true=패(반전, 폼 왕복보정)}],
rank:int(컨텐츠는 null), total_teams:int, notes, videos[{label,type,url}], tags[문자열], owner/시간 4종`
**운영 `/schedules`**: `date, event, members[soop id | "goraesangsa"=전체], groupId?`
**운영 `/contests`**: rework/contests와 동일 스키마(원본, category/tags 없음 → 이관 시 주입)
**`/crews`**: `{pushKey: {aliases[], currentName}}`
**`/status`**: `{members{soopId:{id,name,is_live,title,viewers,thumbnail,live_url}}, updated_at}` — 워커 5분 PUT

**임베드 규칙(`embedUrlOf`, build_archive_detail 인라인)**: 입력 url → `new URL` 파싱 →
host ∈ {`youtu.be`,`youtube.com`,`youtube-nocookie.com`,`sooplive.com`,`sooplive.co.kr`}(정확일치 또는 `.`접미사) →
YouTube: `[\w-]{6,}` videoId 검증 후 `https://www.youtube.com/embed/{id}` / SOOP: `/player/(\d+)` → `https://{host}/player/{id}/embed`.
그 외/파싱실패/비http(s) → null(정적 카드 폴백). **원본 문자열 패스스루 없음(주입 차단).**

## 부록 C. 검증 매트릭스

### C-1. RTDB 규칙 (2026-07-07 11/11 PASS — 재실행용)
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
스크립트는 세션 휘발(scratchpad). "검증 매트릭스 다시 돌려줘"로 재작성. ⚠️§1-1 키 보류 중이라 실행하려면 현행 키 사용(폐기 전).
Phase C 이후 +3종: 무토큰 PUT /status 401, 무토큰 PUT /contests 401, 워커 cron 후 updated_at 갱신.

### C-2. embedUrlOf 보안 (2026-07-08 10/10 PASS — node 재실행용)
`pages/archive-detail.html`에서 `hostMatch`+`embedUrlOf` 추출 → `new Function`/`eval`로 케이스 검증:
| 입력 | 기대 |
|---|---|
| `vod.sooplive.com/player/195579607` | `.../player/195579607/embed` |
| `vod.sooplive.com/player/195579607/`(끝슬래시) | `.../player/195579607/embed` |
| `vod.sooplive.com/player/195579607/embed`(이미embed) | 그대로 |
| `youtu.be/bgNd-gPb_ok?si=xx` | `youtube.com/embed/bgNd-gPb_ok` |
| `youtube.com/watch?v=abc123&t=5` | `youtube.com/embed/abc123` |
| `evil.com/sooplive.com/player/1`(경로위장) | **null** |
| `sooplive.com.evil.com/player/1`(서브도메인위장) | **null** |
| `evilsooplive.com/player/1`(접두위장) | **null** |
| `evil.com/x?u=youtube.com/embed/abc`(쿼리위장) | **null** |
| `javascript:...//sooplive.com/player/1` | **null** |

### C-3. 07-08 회귀 체크 (build 후 자동)
- `python3 src/build.py` → 18페이지 생성 성공.
- 전 페이지 인라인 `<script>` `new Function` 파싱 0 에러(38개).
- 시드 버튼: clips/schedule/notices=0, archive=유지. 죽은 `WHALE_*` 주입 0.
- 멤버 페이지에 옛 placeholder 부서(영업부/기획실 등) 0.
- 클립 폼 `tags`, 아카이브 폼 `tags`+`category` 존재. 칩 `data-f`=all/크루대전/컨텐츠.

## 부록 D. 명령어 치트시트

```bash
# 빌드(18페이지 재생성 — pages/ 직접 수정 금지)
python3 src/build.py
# 로컬 미리보기 (리워크 루트) — 화면 안 바뀌면 Ctrl+Shift+R
python3 -m http.server 8792
# 푸시 (브랜치명 정리 전)
git push origin Test_version:main
# 워커 신규 엔드포인트 생존 확인 (401/400이면 정상)
curl -s -o /dev/null -w "%{http_code}" -X POST https://whale-status-worker.kyefyx.workers.dev/auth/firebase
# RTDB 컬렉션 건수 훑기
curl -s "https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/rework.json?shallow=true"
# embedUrlOf 보안 재검증(부록 C-2) / 규칙 매트릭스(부록 C-1)
#   → "임베드 보안 테스트 돌려줘" / "검증 매트릭스 다시 돌려줘"
```
