# 고래상사 리워크 — 로드맵 v4.0 (2026-07-18 용량·부하 검수판)

> 리워크가 운영(goraesangsa.com)을 대체하는 순간(cutover)까지, 그리고 그 이후의 전체 계획.
> 각 항목에 **실행자 / 선행조건 / 절차 / 합격 기준**을 명시한다. 진행하면서 체크박스를 갱신할 것.
> v3(2026-07-08): 멤버 직급 동기화·아카이브 태그/카테고리·시드 제거·임베드 보안강화 반영 +
> 데이터 사전·검증 명세·이관 경로를 진행분만큼 재구체화. (v2=2026-07-07 실측 구체화, v1=2026-07-07 최초)
> **v3.1(2026-07-11 해체분석 정합화)**: §2.5 완료분을 본문에 역반영 — 런북 4-2의 취소된 일정이관 제거,
> §1-4→4-5-0 흡수, §3-B `/ranking`→stats 교정, §3-D·§5-4 완료 표기, 2-A-2/5 상태 갱신, 부록 C-3/D 19페이지·`git push` 갱신.
> **v3.2(2026-07-12)**: 전수 재검증 스냅샷(§0-5) + 담금질 2차 백로그 §2.6(전부 선택, 실행자/절차/합격 명세) +
> D-Day까지 주차 계획·당일 타임라인(§4-0) + §5 백로그를 Phase C~F 실행 명세로 승격.
> **v4.0(2026-07-18 용량·부하 검수판)**: §8 신설 — 실트래픽(월 1,591명/3,104PV)·RTDB 실측 payload 기반
> 읽기/쓰기/트래픽/무료플랜 전수 검수 + 50인 동시수정 시나리오 + 성장 한계선 계산.
> 결론을 §5에 역주입(C+ 스팸방어 상세, E-7~9 성장 대응, F-6 쿼터 모니터링) + Q7 신설 + 리스크 3종 추가.
> og 7종 삭제사고 복원(og_images.py 재생성 + og.png git 복원, §0-6).

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
| **07-11 해체분석 (v3.1)** | 런북·문서 정합화 + 실버그 수정: KST 날짜 3곳, 이관버튼 멱등화(클립 url·아카이브 제목+날짜 dedup)+아카이브 이관 4필드 주입, 4폼 더블클릭 가드, 상세 5p noindex, dev/실로그인 401 안내 분기, 데모 시드 영업부 교정 | `51f2eb1` |
| **07-11 디자인 2R (§2.5-8)** | 듀얼 critique 27/40 + 접근성·모션 11건 + 백로그 4건(clip-path 와이프·IO 리빌·pg-head 스태거·헤더 바로가기·인사기록카드) | `87b3403`·`605465e` |
| **07-12 디자인 3R (uiuxmax+21st)** | 17항목: 공개화면 이모지→Lucide SVG 전면, 셔머 구현, 필름 그레인, 커서 스포트라이트, 히어로 캐스케이드+일정 스트립(오늘 방송=CTA 글로우), 워터마크 패럴랙스, SEC02 진행바, View Transitions, Pretendard dynamic-subset, CDN SRI+버전고정, jQuery 제거, 스킵링크+`<main>`, 터치타깃 44px, 리빌 .65s, og.png 1200×630 신규 | `2cf1c16` |
| **07-12 디자인 4R (체감 품질)** | 7항목: 런타임 6페이지+홈 **스켈레톤 로딩**(.skel 셔머, CLS 자리 예약) · 목록 이미지 lazy/decoding · **tabular-nums 전역**(body) · 멤버카드 **3D 틸트+글레어**(hover+PRM 가드, is-tilt) · **press scale 피드백**(:active .97) · **공유 요소 전환**(멤버카드→상세 초상 member-hero, 클릭 시 JS 부여+상세는 CSS 고정) · **빈 상태 고도화**(클립/일정/공지/아카이브 아이콘+제목+안내 .n-empty). 검증: ast+재빌드 19p·인라인 45스크립트 node --check 0실패·HTTP 20/20. **재검토 보완**: 실패경로 전수감사 후 상세 3종·멀티뷰 대기실 스켈레톤 + bfcache 전환명 중복(전환 스킵 실버그) 수정 | `52f3e08`·`2024cd9` |

**`1020030`(2026-07-08) 세부** — 전부 빌드·검증 완료(§부록 C-2):
- **멤버 16인 직급/부서/순서 동기화**(§2-A-1 완료): placeholder(영업부·기획실·방송팀 등 가공 부서) → 운영본 조직도(2026-06-08 진급 반영본)의 실제 임원/비서부/게임부/컨텐츠부로 교정. 셀키=인턴(옛 "총무부장" 오류)·멜로딩딩=비서부 부장(옛 "방송팀장" 오류) 등 다수 수정. `rank` 재부여(임원0~/부장10~/사원20~/인턴30~).
- **아카이브↔클립 태그 연결**(§2-A-6 NEW): 클립·아카이브 폼 양쪽에 `tags`(쉼표→배열) 필드. 아카이브 상세가 `D.list('clips')` 후 **태그 교집합(대소문자 무시)** 클립을 "관련 클립" 섹션에 **임베드 미리보기**로 렌더.
- **임베드 미리보기 `embedUrlOf`**(운영 `contest.js getEmbedUrl` 이식 + 보안강화): YouTube·SOOP VOD를 플레이어 임베드로 변환해 **별도 썸네일 이미지 불필요**. ⚠️보안: `new URL` 파싱 + 호스트 엄격검증(정확일치/`.`접미사)으로 iframe src 주입 차단 — `youtube.com/embed/{검증id}`·`*.sooplive.*/player/{숫자}/embed`로만 재조립(원본 패스스루 제거).
- **아카이브 분류(크루대전/컨텐츠)**(§2-A-7 NEW): 폼에 `category` select + 크루전용 필드(순위/상대/게임) 동적 토글. 리스트 필터 칩(전체/🏆크루대전/🎬컨텐츠), 카드·상세 조건부 렌더(컨텐츠는 순위·전적 배지 대신 카테고리 배지). 기존 15건은 category 없음 → **크루대전으로 기본 처리**(하위호환).
- **시드 불러오기 제거**(클립·일정·공지): cutover 전엔 401만 유발 + 실데이터도 아니므로 삭제. 버튼·`importSeed`·죽은 `window.WHALE_*` 주입·`clips_json_script`/`schedule_json_script`/`notices_json_script` 함수까지 정리. **아카이브 운영기록 이관 버튼은 유지**(실데이터 마이그레이션 경로).
- **stale 주석 최신화**: 아카이브 docstring(크루대전→통합), 상세("대회"→"기록"), content JSON `_comment`(clips/schedule/notices — 이제 실 페이지는 Firebase 렌더, 이 JSON은 admin 데모·뉴스 피드 미리보기 전용).
- **뒷정리**: 노출된 서비스계정 키 JSON 삭제(§1-2 완료).

**Phase B 구성** (전부 배포·검증 완료):
- 워커 `POST /auth/firebase` (`whale-status-worker.kyefyx.workers.dev`, 소스 `03_WCHP/whale-auth-worker/worker.js` — 레포 밖):
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
  연결된 Vercel 계정·GitHub 레포는 **미확인**(§6-Q1). 운영 코드 로컬 사본 = `03_WCHP/Whale-Corp-main/`.
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
- 레포: `github.com/HotCake0/Test_version`. ✅**로컬 브랜치도 `main`**(1-3 완료, 2026-07-10) → 푸시는 `git push`.

### 0-4. 리워크 데이터 스키마 (부록 B에 전체 사전)
- 시드 단일소스: `src/content/{members,clips,schedule,notices,site}.json` → `python3 src/build.py` → `pages/*.html`.
  **pages/는 산출물 — 직접 수정 금지, 수정은 build.py/JSON에만.**
- ⚠️07-08 변경: `clips/schedule/notices.json`은 이제 **admin 데모 페이지·뉴스 피드(news) 미리보기 전용 정적 시드**.
  실 clips/schedule/notices 페이지는 Firebase(`WhaleData.list`)에서 렌더하며 이 파일을 안 씀(시드 불러오기·`WHALE_*` 주입 제거됨).
  `members.json`만 여전히 빌드타임 실렌더 소스(crew/members/member + multiview·news의 멤버 메타).
- CRUD 런타임 스키마는 각 폼이 정의(부록 B). 공통 자동 필드: `ownerId, ownerNick, createdAt, updatedAt`.

### 0-5. 2026-07-12 전수 재검증 (v3.2 스냅샷)
- **빌드 재현성 PASS**: `python3 src/build.py` → 19페이지 재생성, `git diff` 0건(pages/ = build.py 완전 동기).
- **JS 구문**: `node --check assets/site.js` PASS. 워킹트리 클린(main = origin/main `63670f4`).
- **RTDB 실측 = 계획과 정확 일치**: `/rework` = {contests 15, notices 1(dev "테스트" — 4-5-0 삭제 예정)},
  clips/schedules 비어 있음. 운영 contests 15 = rework 15(**diff 0** — 아카이브 이관 버튼은 "이미 모두 있음"이 정상).
- **인프라 생존**: 워커 `/auth/firebase` 401(정상), apex→www 307, `www.goraesangsa.com` 200.
- 결론: **cutover 선행조건·필수 작업 잔여 0.** 남은 것 = §2.6(전부 선택) + §4 런북(8/3) + Q6(보류).
- **07-13 갱신**: §2.6 Claude 몫 전부 소진(2.6-8 critique 26/40·P1 0건 완료). 잔여 = 2.6-9 리허설(D-1, 사용자)·2.6-10 Q6 재상신(D-7)·§4 런북뿐.

### 0-6. 2026-07-18 스냅샷 (v4.0)
- **실트래픽 확보(Vercel Analytics, 최근 30일)**: 방문자 **1,591명**(-29%), 페이지뷰 **3,104회**(-45%), 이탈률 66%.
  일평균 ~53명/103PV, 피크일 ~110명. 이 수치가 §8 용량 검수의 기준선.
- **워킹트리 사고 복구**: og 7종이 삭제된 채 발견(폴더 개명 `04_WCHP`→`03_WCHP` 여파 추정) →
  `src/og_images.py` 재실행으로 6종 바이트 동일 복원 + 홈 `og.png`는 git HEAD에서 복원. 경로수정(04→03) 2파일은 커밋 반영.
- **RTDB payload 실측(curl, §8-1 표)**: 운영+rework 전체 합산 **~39KB** — 텍스트 전용이라 극소.
- 코드 프리즈 유지(2.6-8 이후 코드 무변경). §8 검수 결론: **D-Day 전 코드 변경 불필요** — 용량 대응은 전부 cutover 후 Phase에 배치.

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
- [~] **1-4. dev 테스트 공지 삭제** — `/rework/notices`의 "테스트" 1건(ownerId `dev:핫케이크_`).
  규칙 강제로 이제 콘솔 외엔 admin 토큰 필요 → **D-Day 런북 §4-5-0으로 이관 확정(2026-07-11)**: 실로그인 검증 직후 admin UI에서 삭제(개시 공지 게시 전). 앞당기고 싶으면 사용자가 Firebase 콘솔 데이터 탭에서 노드 삭제해도 됨.

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
- [~] **2-A-2. 클립 실데이터** — `/rework/clips` 비어 있음. ✅**경로 확정(07-11, §2.5-4)**: 클립 페이지 관리자 전용 "운영 아카이브에서 클립 불러오기" 1클릭 버튼 구현(13건±, 런북 §4-5-5에서 실행). 추가 클립은 (b) UI 직접 입력. 아래는 이력 보존:
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
- [x] **2-A-5. 뉴스 피드** — ✅**2026-07-11 런타임 전환 완료(§2.5-3)**: news.html이 `D.list('notices'|'clips'|'schedules')` 실데이터 렌더(고정공지 히어로·최신 클립 5·다가오는 일정 5, 패널별 빈/실패 문구). 정적 시드는 admin 데모 미리보기 전용으로만 잔존.
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
- [x] **2-B-3. SEO/메타 일괄** ✅**2026-07-10**(favicon·description·og·twitter) + ✅**07-11 canonical 완료**(라우팅 확정 후 잔여분): BASE_URL을 정식 호스트 `www`로 교정, 전 페이지 `<link rel="canonical">`(cleanUrls 무확장), admin 페이지 `noindex,nofollow`, **robots.txt**(admin·auth 차단)+**sitemap.xml**(build.py 자동 생성, 진입점 10URL)+**브랜드 404.html**(자립형, 세계관 카피) 신설. apex→www 307 실측 확인 — 실행자: Claude. build.py `head()`(build.py 49행)에 페이지별
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

- [x] **2.5-1. impeccable 재-critique** ✅**2026-07-11 완료 — 26/40 (Acceptable, 이전 25)**. 듀얼 에이전트(디자인 리뷰+검출기). 검출기 53건 중 진성 5건(em-dash 케이던스·layout-transition), 오탐/의도 48건(단일폰트=외부CSS 미추적 오탐, GNB 넘버링=기능적 색인, 호버 글로우=피드백).
  **당일 후속 수정 완료**: ①[P1] admin 대시보드 거짓 "데모 환경" 문구 제거+통계 D.list 실카운트+게이트 폴링→authchange 이벤트 ②[P2] 홈 가짜 "이번 주 일정" 4건→`/rework/schedules` 런타임(다가오는 4건, textContent 조립, ScrollTrigger.refresh) ③[P2] 모바일 .n-btn 터치타겟 40px ④전역 focus-visible 링(:where 특이도0, 카드 위젯 포함) ⑤layout-transition 4곳 padding-left→transform ⑥와이어프레임 링크 전면 제거+`.vercelignore` 신설(와이어프레임/src/ROADMAP 등 배포 제외) ⑦아카이브 폼 승/패 파싱 silent failure→명시 검증+안내 ⑧시드 클립 제목 em-dash 케이던스 9건 리라이트.
  **남은 감점 요인(후순위 기록)**: 헬프/단축키/일괄작업 부재(H10=1점, §5-3), pg-eyebrow+EN 아웃라인 헤더 18페이지 반복(admin만이라도 분기 검토, §5-3 admin 실연동 때), og:image 페이지별 차별화(§5-4), confirm/alert 네이티브 다이얼로그 톤(§5-4), 동시편집 last-write-wins(§5-2).
- [x] **2.5-2. ranking 통계 재구현** ✅**2026-07-11 완료** — `pages/stats.html` 신설(build_stats, 19페이지째). 운영 ranking.js 로직 이식: 요약 타일 4종(크루대전 수·게임 수·게임 승률·참여율 1위) + 사원별 성적(참여율 바+승률 뱃지) + 게임별 승패 + 상대 크루 전적(crews currentName·과거명 title). **Chart.js 의존 제거**(리워크 토큰 CSS 바). category=컨텐츠 제외 집계, 다자전 rank 규칙, GNB 3-2(드로어+홈 손수정 양쪽), `/ranking` 리다이렉트 목적지 stats로 교체. 실데이터 15건 node 시뮬레이션 검증(15전·32게임 53%·울산큰고래 87% 출전).
  - ⭐**부수 발견·수정: opponents.result 반전 버그** — 데이터사전의 "true=패" 기록이 오독이었음(운영 admin.js `isWin` 규약=true=승, 실데이터 15건 교차검증). 이전 렌더가 **우승 기록 5건을 '패'로 표시**하던 실버그 → 아카이브 렌더/폼 파스/직렬화/부록B 전부 true=승으로 교정.
- [x] **2.5-3. news 피드 런타임 전환** ✅**2026-07-11 완료** — build_news()를 `D.list('notices'|'clips'|'schedules')` 런타임 렌더로 교체. 히어로=고정공지 우선(없으면 최신), 클립=createdAt 최신 5, 일정=오늘 이후 5. 패널별 빈 문구·실패 문구, `.news-empty` 스타일. 시드 상수는 news에서 미사용(다른 페이지 미리보기는 유지). node --check 통과.
- [x] **2.5-4. 콘텐츠 사전 준비** ✅**07-11 완료** — 개시 공지 초안 2종 + **클립 자동 이관 버튼 구현**(사용자 "운영 아카이브 클립만 찾아서" 지시).
  - **클립 불러오기(§2-A-2 해소)**: clips 페이지에 관리자 전용 "운영 아카이브에서 클립 불러오기" 버튼(⚠️07-11 개선: 목록 빈 경우 한정→**항상 노출·URL 중복 스킵 멱등**, 더블클릭 가드, 부분 실패 집계+재시도 안내). 클릭 시점에 운영 `/contests`의 videos 중 라벨 '클립'/'편집' 포함만 추출해 일괄 `D.create`(현재 13건: 클립 12+편집영상 1, 같은 대회 다건은 자동 번호). category=대회, creator=고래상사, desc=대회 날짜, **tags=[대회 제목]**(비노출 — 아카이브 기록에 같은 태그를 달면 상세 '관련 클립' 자동 연결). 실데이터 추출 시뮬레이션 13건 검증.
  - ⚠️실행 시점: Claude는 쓰기 수단 없음(키 삭제) → **cutover 후(또는 운영 도메인에서) 관리자 로그인 → 클립 페이지에서 1클릭**. D-Day 런북 §4-5 직후 권장.
  - **초안 A(정식 톤)**: 제목 "고래상사 홈페이지가 새로워졌습니다" / 본문: 새 단장 안내 → 멤버·일정·클립·아카이브 소개 → 멀티뷰 실시간 안내 → 오류 제보 요청. pinned ✅.
  - **초안 B(세계관 톤)**: 제목 "[사내 공지] 고래상사 신사옥 입주 안내" / 본문: 신사옥 이전 → 전 직원(16명) 프로필·근무 일정·업무 성과 열람 → CCTV(멀티뷰) 안내 → 하자 제보는 관리부(방송 채팅). pinned ✅.
  - 입력: cutover 후 admin 로그인 → 공지 작성 → 상단 고정 체크(news 히어로 자동 노출).
- [x] **2.5-5. 미세정리 일괄** ✅**2026-07-11** — crew 프로즈 "사장부터 인턴까지·비서/게임/컨텐츠"로 교정(build.py+재빌드). ~~admin-* 옛 부서명은 조사 결과 이미 없음~~ ⚠️정정(07-11 재감사): 데모 시드 제목/설명에 존재하지 않는 "영업부" 7곳 잔존했음(archive/clips/schedule.json) → 게임부·컨텐츠부로 교정 완료. index 466px는 취약한 손수정 메인이라 **의도적 미수정 유지**(2-B-1 결론 준용, 시각적 깨짐 없음).
- [~] **2.5-6. D-Day 리허설** — ❌**취소(2026-07-11 사용자 결정)**: 리허설 없이 8/3 오전 전환+데이터 입력 일괄 수행(§4 참조). 아래 절차는 필요 시 참고용 보존: 본인 Vercel 계정에 `Test_version` 별도 import → 임시 `*.vercel.app`에서 vercel.json 리다이렉트·cleanUrls·전 페이지 실배포 검수(§4-4 사전 수행, 실로그인만 제외). 리허설 후 프로젝트 삭제.
- [x] **2.5-7. 실기기 모바일 최종 확인**(사용자) ✅**2026-07-11 통과** — 실기기 확인 결과 양호. 후속 조치 1건: **모바일(≤768px) 인트로 생략**(`921c941`, 즉시 히어로·터치 스크롤 잠금 제거).
- [x] **2.5-8. 디자인 critique 2R + 백로그 전량 구현** ✅**2026-07-11 저녁** — 듀얼 에이전트 critique **27/40**(스냅샷 `.impeccable/critique/2026-07-11T14-28-50Z__index-html.md`).
  - 1차 수정(`87b3403`): [P1] js-anim 무JS 폴백 배선(리빌 opacity:0 → JS 실패 시 빈 화면 리스크 제거)·모달 포커스 이동/Tab순환/복귀(role=dialog 공통)+드로어 포커스 / 리빌 once-only / smooth scroll·GNB 서브메뉴 PRM 게이팅 / 100svh 폴백 순서 / placeholder 4.5:1 / 공지 본문 70ch / 칩 모바일 40px / stats 참여율 바 상태색 오용 제거.
  - 2차 백로그(`605465e`): [P2] 대각선 와이프 border-width→**clip-path**(updateOverlays JS 폐기)·스크롤 리빌→**IntersectionObserver**(once-only, 폴백 유지) / [P2] pg-head 3단 스태거(eyebrow→EN 좌슬라이드→부제) / [P3] 멤버 모달 스탯 "인사기록카드·대외비" 세계관 프레임 / [P3] 데스크톱 헤더 중앙 소식·일정·멀티뷰 상시 노출(.h-nav, 현재 섹션 표시).
  - 사용자 로컬 확인 통과("낫배드", 07-11). 잔여 소소분(§5 백로그): 필터 URL 동기화·dead CSS 정리·stats 오류문 순화.
- ⏸ (보류 유지) §1-1 키 교체 — 사용자 결정. D-Day 전 재개 권장 입장만 보존.

---

## 2.6. 담금질 2차 백로그 (v3.2 신설 — 2026-07-12 ~ 08-02, D-22)

> §0-5 재검증으로 필수 작업은 잔여 0 — 여기 항목은 **전부 선택(opt-out)**: 하나도 안 해도 8/3 런북에 지장 없다.
> 07-11~12 critique·디자인 3R에서 "후순위 기록"으로 남긴 잔여분을 실행 가능한 명세로 승격한 것. 우선순위순.

**주차 배치 권장**: W-3(07/13~19) = 2.6-1~5 · W-2(07/20~26) = 2.6-6~7 · W-1(07/27~08/02) = 2.6-8~9 + Q6 재상신 → D-Day 08/03.

- [x] **2.6-1. 히어로 일정 스트립 LIVE 실판별** ✅**07-12 완료(`1a35c88`)** — /status 실측 승격, 실패 시 추정 폴백, textContent 조립.
  - 현황: `#heroStrip`의 "오늘 방송" 판별이 `/rework/schedules` 일정 기반 **추정**(실제 방송 여부 모름).
  - 절차: index.html 인라인 homeSched fetch에 `/status.json` 병행 fetch → 오늘 일정 멤버 중 `is_live` 존재 시
    is-today 펄스를 "LIVE" 확정 표기(+시청자수)로 승격, status 실패 시 현행 추정 폴백 유지.
  - 주의: index는 손수정 파일 — 인라인 JS 수정 후 정규식 추출→`node --check`(07-11 검증 패턴 재사용).
  - 합격: 방송 중 멤버 존재 시 스트립 LIVE 실표기, 오프라인 시 "다음 방송" 회귀 없음, 콘솔 에러 0.
- [x] **2.6-2. 클립 인라인 재생** ✅**07-12 완료(`1a35c88`)** — embedUrlOf→site.js `WhaleEmbed` 승격(아카이브 상세는 참조로 교체), 클립 상세 임베드 플레이어. **C-2 매트릭스 10/10 PASS(이제 site.js 대상)**.
  - 절차: `embedUrlOf`를 `assets/site.js` 공유 헬퍼로 승격 → clip 상세 본체 큰 플레이어를 임베드 렌더로
    (현재 외부 링크) → 아카이브 상세는 공유판 참조로 교체. ⚠️`_CLIP_JS_SHARED`는 비raw 문자열 — JS `\n`은 `\\n`.
  - 합격: 재빌드 19p + 부록 C-2 10케이스 재실행 PASS(위장 url 전부 null) + 클립 상세 인라인 재생.
- [x] **2.6-3. 필터 URL 동기화** ✅**07-12 완료(`1a35c88`)** — 클립·공지(동적 칩, 무효값 방어)+아카이브(정적 칩 2종 화이트리스트), replaceState+진입 복원.
  - 절차: clips/archive/notices 필터칩 선택을 `?f=` 쿼리로 `history.replaceState` 반영 + 진입 시 복원.
  - 합격: 필터 상태로 새로고침·URL 공유 시 동일 필터 착지, canonical은 쿼리 무시(기존 태그 유지).
- [x] **2.6-4. dead CSS 정리 + stats 오류문 순화** ✅**07-12 완료(`1a35c88`)** — stats err.message 노출→고정 안내문. dead CSS는 조사 결과 후보(.project_title 등)가 **실존 마크업의 의도적 숨김**이라 제거 보류(취약한 손수정 홈, 실익 없음).
  - 절차: 옛 pin/커서라벨 등 미참조 셀렉터를 grep 교차확인 후 제거(홈 인라인+site.css 양쪽),
    stats `err.message` 노출 → "데이터를 불러오지 못했습니다. 잠시 후 새로고침해 주세요." 고정 문구.
  - 합격: 재빌드 후 전 페이지 육안 회귀 없음(로컬 8792 스팟), 삭제 셀렉터 참조 0 재확인.
- [~] **2.6-5. 그레인·셔머 강도 튜닝** — **현행 유지(07-12, 권고대로 무피드백=승인 범위)**. 사용자가 "더 약하게/세게" 한마디 주면 수치 1~2곳 조정.
  - 절차: 사용자가 로컬 확인 후 "그레인 더 약하게/세게, 셔머 빠르게/느리게" 한마디 → `body::after` opacity(.04)·
    셔머 duration 수치 조정. 무피드백이면 현행 유지(이미 승인 범위).
- [x] **2.6-6. og:image 페이지별 차별화** ✅**07-12 완료(`1a35c88`)** — 그룹 6종(crew/archive/clips/schedule/multiview/notice) PIL 생성 총 302KB, head() 슬러그→그룹 분기(14페이지), 홈·admin은 og.png 유지.
  - 절차: 07-12 og.png 생성 파이프(PIL+malgun, 1200×630) 재사용 → 그룹 5종(크루/아카이브/클립/일정/소식) 파생
    `og-{group}.png` 생성 → build.py `head()`에서 그룹별 분기. 홈은 현행 og.png 유지.
  - 합격: 총량 증가 <600KB, 카톡 디버거(또는 meta 육안)로 그룹별 상이 확인.
- [x] **2.6-7. Lighthouse 기준선 측정** ✅**07-12 완료** — 로컬 http.server(무압축·무캐시=보수적 기준선), 모바일 프리셋, 순서 perf/a11y/bp/seo:
  **home 79/96/100/100 · members 85/95/100/92 · clips 61/95/100/100 · schedule 83/95/100/100 · stats 73/92/96/100**.
  Vercel 배포판은 압축·CDN으로 perf가 이보다 높게 나옴 — cutover 후 동일 페이지 재측정해 회귀 비교(§5-5 F-4).
  - 절차: 무sudo Chromium(2-B-2 방식) + lighthouse CLI(포터블 node)로 홈+대표 4페이지 성능/접근성/BP/SEO 측정
    → 수치를 이 문서 부록에 기록. cutover 후 동일 조건 재측정해 회귀 감지.
  - 합격: 4지표 수치 기록(목표 제시용 — 이 시점 수정은 안 함).
- [x] **2.6-8. 디자인 최종 critique** ✅**07-13 완료 — 26/40, P0/P1 0건(합격 조건 충족)**. 코드 프리즈 상태라 W-1을 앞당겨 수행.
  듀얼 에이전트(A 디자인리뷰·B 검출기, 격리). 스냅샷 `.impeccable/critique/2026-07-13T09-25-16Z__index-html.md`.
  - A의 P1 2건은 부모 검증에서 격하/기각: ①인트로 스킵 발견성 → 최초 1회+모바일 생략+즉시 노출+대비 8:1이라 P3 ②핀 진행바 부재 → **기각, 이미 존재**(index.html `.pin-bar`+`#pinBarFill`, 3R `2cf1c16`).
  - B: 검출기 51건 사실상 전부 오탐(GNB 넘버링 중복계상·외부CSS 미인식·호버글로우 복제·JS주석 em-dash). 콘솔 에러 0(5p), 실질 대비위반 0, 포커스 링 15/15, 모바일 오버플로 무해(닫힌 드로어, overflow-x:clip).
  - P2 이하는 §5-4 E-6로 기록. **W-1에는 재critique 불필요 — 이후 코드 변경 시에만.**
- [ ] **2.6-9. 런북 문서 리허설** (P1, 사용자+Claude, D-1 권장, ~30분) — 실전환 없는 자리 확인.
  - 절차: §4를 함께 읽으며 사용자 콘솔 몫의 화면 위치를 사전 확인 — Vercel(Settings→Git→Disconnect/Connect),
    Firebase(RTDB 데이터 탭→⋮→JSON 내보내기), SOOP 로그인 계정 준비. 소요·순서 최종 점검.
  - 합격: 사용자 "당일 헤맬 곳 없음" 확인. (2.5-6 배포 리허설 취소와 별개 — 이건 문서·화면 확인만.)
- [ ] **2.6-10. Q6 키교체 재상신** (W-1) — 보류 존중하되 D-7에 1회만 재확인. 근거: `/rework`가 실서비스로 승격되는
  순간 노출키(§1-1)의 영향 범위가 "격리 경로"에서 "정식 데이터"로 커짐. 거절 시 §5-5 로테이션으로 최종 이관.

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
  | `/ranking` | `/pages/stats` | ⭐07-11 stats 신설(2.5-2)로 목적지 교체 완료(`25bb120`) — 아래 JSON은 초안, **레포 루트 vercel.json이 정본** |
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
      { "source": "/ranking",  "destination": "/pages/stats",   "permanent": true },
      { "source": "/ranking.html",  "destination": "/pages/stats",  "permanent": true },
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
- [~] **아카이브 재이관**: ✅**07-11 '운영 기록 불러오기' 버튼을 diff 이관으로 승격** — 제목+날짜가 같은 기록은 스킵(멱등)하고 누락분만 등록하며, `category:"크루대전"`·`tags`·`notes`·`total_teams`까지 주입(기존 구현은 이 4필드를 떨어뜨렸음 — notes는 상세에 렌더되는 필드라 실손실이었음). 이제 **스크립트 불필요** — D-Day에 admin 로그인 후 아카이브 페이지에서 1클릭(런북 4-5-6). 실측: 현재 diff 0건(15=15), 운영 추가분 발생 시 자동 포착. 수정(변경)분 diff는 미탐지 — 필요 시 수동 대조.
- [ ] **일정 이관**: §2-A-4 매핑대로 (D-Day 단계).
- `/crews`(상대크루 사전)는 그대로 사용(공개 읽기 유지 — 아카이브 상세가 참조).

### 3-D. 운영 전용 기능 인수인계 (✅ §6-Q4 확정 — 2026-07-10 사용자 "권장으로 진행")
| 운영 기능 | 리워크 현황 | 결정 |
|---|---|---|
| ranking.html — 멤버 참여율/승률 통계, 현역 필터 | ✅**재구현 완료(07-11, 2.5-2)** — `pages/stats.html` | **ⓐ 채택 후 앞당겨 완료**: `/ranking`→`/pages/stats` 리다이렉트로 연결(공백 기간 없음) |
| admin.html — 기간 반복 일정(groupId 일괄), 멤버 직급색 관리 | admin-*는 데모 목업. 일정 CRUD 단건만 | **ⓑ 채택**: 단건 유지·포기. 반복 입력 실수요 확인되면 §5-3 재검토 |
| image-protect.js — 우클릭/드래그 저장 방지 | ✅**ⓐ 이식 완료(2026-07-10)** | site.js IIFE 끝부분 + index.html 인라인(홈은 site.js 미로드) 두 곳. IMG 한정 contextmenu/dragstart 차단 |
| 워커 cron 5분 `/status` 갱신 | 리워크 멤버/멀티뷰가 동일 소스 사용 | **그대로 유지(무변경)** |
| update_status.py (수동 갱신) | 워커 cron이 대체 | 폐기 |

---

## 4. Cutover 실행 런북 (D-Day = **2026-08-03 확정, 오전 작업** — 07-11 사용자 결정: 사전 리허설 없이 전환+데이터 입력(클립 이관 1클릭·개시 공지·일정)을 당일 오전에 일괄 수행)

> 예상 소요 1~2시간 + 24시간 집중 관찰. 방송 없는 낮 시간대 권장.
> 사전조건: §2-A-2/3(클립·공지 준비 ✅), §3-A/B/D 결정 ✅, vercel.json 커밋 ✅. §1-4 테스트공지 삭제는 **4-5-0으로 흡수**(admin UI가 열리는 시점이 D-Day라 당일 처리가 최단). (§1-1 키교체는 사용자 보류 상태 — cutover 전 재개 권장하나 blocker 아님.)

### 4-0. D-Day 당일 타임라인 (v3.2 — 권장 시각·소요)

| 시각 | 단계 | 실행자 | 소요 | 비고 |
|---|---|---|---|---|
| 09:00 | 4-1 백업(운영 태그/zip + RTDB export) | 사용자+Claude | 15분 | export 파일 최상위 키 6종 확인 |
| 09:15 | 4-3 Vercel 연결 레포 교체(시나리오①) | 사용자 | 10분 | Framework=Other, Output=`/` |
| 09:25 | 4-4 스모크(19p 200·리다이렉트 6종·status 렌더) | Claude | 15분 | 실패 시 즉시 4-7 판단 |
| 09:40 | 4-5-0~4 실로그인 검증(테스트공지 삭제 포함) | 사용자+Claude | 20분 | Phase B 첫 실전 — 실패 시 Claude 진단 |
| 10:00 | 4-5-5/6 클립 이관·아카이브 diff 1클릭 | 사용자 | 5분 | 멱등 — 부분 실패 시 재클릭 |
| 10:05 | 개시 공지 게시(초안 A/B 중 택1, pinned)+예정 일정 입력 | 사용자 | 20분 | news 히어로 자동 노출 확인 |
| 10:30 | 4-6 모니터링 개시 | Claude+사용자 | 24h 집중 | 롤백 트리거 3종 감시 |
| (실패 시) | 4-7 롤백 = Vercel Instant Rollback | 사용자 | 5분 | 데이터는 그대로 둬도 안전 |

- [ ] **4-1. 백업 (T-0h)** — Claude + 사용자
  - 코드: 운영 레포에 태그 `prod-final-YYYYMMDD` (또는 로컬 `Whale-Corp-main` zip — 이미 로컬 사본 있음).
  - 데이터: RTDB 전체 export — Firebase 콘솔 → RTDB → 데이터 탭 → ⋮ → "JSON 내보내기"
    (또는 Claude가 `GET /.json` 덤프). **합격: 파일 열어 최상위 키 6종 확인.**
- [ ] **4-2. 데이터 최신화** — ⚠️07-11 재설계: Claude는 쓰기 수단 없음(키 삭제) → **전부 4-5 실로그인 후 UI 1클릭/입력으로 이동**
  - §3-C 아카이브 diff 재이관 → **4-5-6 '운영 기록 불러오기' 버튼**(07-11 diff·멱등 승격, category/tags/notes/total_teams 주입).
  - ~~일정 이관 73건~~ **취소됨(Q2, 2026-07-10)** — 일정은 4-5 실로그인 후 관리자 UI로 **예정 일정부터 신규 입력**(§2-A-4 참조).
  - Claude 몫은 사전 검증뿐: 운영/rework 건수 대조 curl(부록 D) + 버튼 시뮬레이션은 07-11 완료.
- [ ] **4-3. 배포 전환** — 사용자(Vercel 콘솔) — §3-A 결정 시나리오 실행.
- [ ] **4-4. 스모크 테스트 (전환 직후 10분)** — Claude(curl+Playwright)
  - `https://www.goraesangsa.com/` 및 `pages/*` 19페이지 HTTP 200 + 콘솔 에러 0.
  - 리다이렉트 6종(§3-B) 30x → 목적지 200. apex→www 유지. `/auth/callback` 200(코드 없이=문구 정상).
  - `/status` 데이터로 멀티뷰/멤버 LIVE 뱃지 렌더(워커 cron 무영향 증거).
  - **NEW: 아카이브 카테고리 칩 필터 동작 + 관련클립 임베드 렌더 스팟 체크.**
- [ ] **4-5. 실로그인 검증 (사용자 + Claude 안내)** — **Phase B의 첫 실전 검증 지점**
  0. **§1-4 처리**: admin 로그인 상태에서 `/rework/notices`의 dev 테스트 공지("테스트", ownerId `dev:핫케이크_`) 삭제 — 개시 공지 게시 전에 먼저.
  1. 관리자(울산큰고래 or editor 핫케이크_) SOOP 로그인 → Session Storage `soop_user`(role) + `soop_fb`(idToken) 확인.
  2. 공지 작성→수정→pinned 토글→삭제 / 클립 작성→featured 토글→**태그 넣고 관련아카이브 노출 확인** / 일정 작성 / 아카이브 수정→**카테고리 전환 확인**. 전부 성공.
  3. 일반 SOOP 계정(권한 미등록) 로그인 → 본인 글 작성/수정 성공, 남의 글 버튼 미노출.
  4. (심화) 일반 계정 콘솔 강제 호출: `fetch('.../rework/notices/<남의글키>.json?auth='+idToken,{method:'DELETE'})` → 401.
  - **실패 시**: `soop_fb` 없음=교환 실패(워커/키), 쓰기 401=토큰첨부/규칙. Claude 호출 진단.
  5. **클립 일괄 이관(§2.5-4)**: 검증 성공 직후 admin 상태로 클립 페이지 → "운영 아카이브에서 클립 불러오기" 1클릭 → 13건± 등록 확인. (07-11 멱등화 — URL 중복 스킵, 부분 실패 시 재클릭으로 잔여분만 재시도.)
  6. **아카이브 diff 이관(§3-C)**: 아카이브 페이지 → "운영 기록 불러오기 (누락분 이관)" 1클릭 → 운영 추가분만 등록(0건이면 "이미 모두 있음" 안내가 정상).
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

> **v3.2 Phase 배치 권장안** — 안정 관찰 1주(§4-6/4-8) 후 착수. 각 Phase는 독립적이라 순서 교체 가능하나,
> C(보안)를 다른 것보다 먼저 두는 이유: cutover로 운영본 무토큰 쓰기가 소멸하는 "조일 수 있는 첫 시점"이기 때문.

| Phase | 권장 주차 | 내용 | 항목 | 배포 필요 |
|---|---|---|---|---|
| **C** | D+1~2주 (8/10~) | 운영 경로 보안 강제(워커 SA 인증+규칙) | §5-1 | 워커 1회(사용자)+규칙 게시 |
| **C+** | D+2주 | RTDB 규칙 정제(pinned/featured·validate) | §5-2 | 규칙 게시만 |
| **D** | D+3~5주 | 관리자 페이지 실연동 3종 | §5-3 | push만(+permissions UI는 워커 1회) |
| **E** | 수시(수요 기반) | 기능/콘텐츠 확장 + **성장 대응(E-7~9, 트리거 기반)** | §5-4 | push만 |
| **F** | D+1주부터 상시 | 운영 위생(백업 자동화·키 로테이션·Lighthouse·**쿼터 모니터링 F-6**) | §5-5 | 워커 cron 1회 |

### 5-1. Phase C — 운영 데이터 경로 보안 강제 ⭐권장 1순위
현재 `.write:true`인 4경로를 조인다. 전제: cutover 완료(운영본 무토큰 쓰기 소멸 후).
**v4.0 용량 근거 추가(§8-5 #1)**: 이 경로는 보안 구멍이면서 동시에 **무료쿼터 폭탄 벡터** — 익명 대량 PUT만으로
저장 1GB·다운로드 10GB를 태울 수 있는 유일한 지점. 보안+용량 양면에서 cutover 후 첫 작업으로 유지.
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
- **v4.0 스팸/쿼터 방어 상세(§8-5 #2 해소 — 이 항목의 핵심 승격)**: 현재 임의 SOOP 계정이 상한 없는 크기·개수로
  create 가능 → 무료쿼터 고갈 벡터. 아래 3중 상한을 컬렉션별 `.validate`에 추가(Claude 규칙 작성 → 사용자 콘솔 게시 1회):
  1. **필드 화이트리스트**: `newData.hasChildren([...필수])` + `"$other": {".validate": false}` — 스키마 외 임의 필드 저장 차단.
  2. **문자열 길이 상한**: `title≤200 · creator/cat/category/type/time≤50 · desc/notes≤2000 · body 문단당≤2000·문단수≤50 ·
     url/img≤500 · tags 항목≤30자·개수≤10 · members 항목≤50자·개수≤20` (본문류 넉넉히, 나머지 타이트하게).
  3. **타입 강제**: `pinned/featured` isBoolean, `date` `matches(/^\d{4}-\d{2}-\d{2}$/)`, `createdAt/updatedAt` isNumber.
  - 이 상한으로 항목당 최대 ~10KB — 악성 계정이 수천 건을 넣어도 저장·다운로드 폭탄 불가(건수 rate-limit은 RTDB 규칙로
    불가능하니 개수 폭주는 F-6 모니터링+admin 일괄삭제(D-1)로 대응. 필요시 Q7 결정으로 create를 editor+로 제한).
  - 검증: 상한 초과 payload POST → 401/400, 정상 폼 4종 저장 → 200 (부록 C-1에 +4케이스).
- ownerNick 위조는 무해(판정은 ownerId)라 보류.

### 5-3. 관리자 페이지 실연동 (Phase D — v3.2 실행 명세)
- **D-1. admin-clips/notices(-members) 테이블 실연동** (Claude, ~반나절): 데모 alert → `WhaleData` 실 CRUD.
  - 절차: build.py admin-* 목업 테이블을 `D.list()` 런타임 렌더로 교체(기존 CRUD 페이지 패턴 재사용) +
    체크박스 일괄 선택→일괄 삭제(admin 토큰, 항목별 실패 집계 — 이관 버튼의 부분실패 패턴 재사용) +
    기존 `ADMIN_GATE_JS`·authchange 이벤트 그대로. 데모 시드 JSON은 이 시점 admin에서 용도 소멸(news 미리보기용만 잔존).
  - 합격: admin에서 작성/수정/삭제/일괄삭제 → 공개 페이지 즉시 반영, 일반 계정 접근 시 게이트 차단 유지.
  - 이때 critique 잔여 "admin 헤더 분기"(pg-eyebrow/EN 아웃라인을 admin만 실무형 헤더로)도 함께 처리.
- **D-2. 기간 반복 일정**(옛 admin.js groupId, Q4에서 "수요 확인 시" 조건부): 일정 폼에 "반복(시작~종료/요일)" →
  N건 create에 같은 `groupId`, 수정/삭제 시 "연결 N건 함께" confirm 옵션.
  - **착수 조건**: cutover 후 사용자가 반복 일정을 손으로 2회 이상 입력하는 실수요 확인 시(그 전엔 YAGNI).
  - 합격: 반복 생성 N건 groupId 일치, 단건 수정과 일괄 수정 모두 정상, 캘린더 렌더 회귀 없음.
- **D-3. permissions 관리 UI** (중기): 콘솔 전용인 `/permissions`를 UI로 — 워커 `POST /admin/permissions` 신설
  (idToken 검증→admin claim 확인→§5-1의 SA access_token 재사용해 쓰기). admin-members 페이지에 역할 부여/회수.
  - 배포: 워커 1회(사용자 대시보드). 합격: editor 추가/제거 반영 + "재로그인해야 claim 갱신" 안내 노출(§7 리스크 대응).

### 5-4. 기능/콘텐츠 (Phase E — v3.2 실행 명세, 수요 기반 수시)
- ~~통계 페이지 재구현~~ ✅**앞당겨 완료(07-11, §2.5-2 `pages/stats.html`)**. 잔여: 현역/퇴사 필터 등 세분화는 수요 시.
- ~~news 실데이터 전환~~ ✅**앞당겨 완료(07-11, §2.5-3 런타임 전환)**.
- **E-1. 클립 임베드 플레이어 확대** → **§2.6-2로 앞당김 후보 승격**(cutover 전 가능). 미착수 시 여기 잔존:
  `embedUrlOf`를 site.js 공유 헬퍼로 승격 → 클립 상세 본체 인라인 재생. 합격 = 부록 C-2 재실행 PASS.
- **E-2. 멤버 스탯 실데이터** (Claude 코드 + 사용자 워커 배포, ~반나절): 현재 멤버 모달/상세 스탯 = 세계관 placeholder
  ("인사기록카드" 프레임으로 완화된 상태 — critique 판정). 워커 cron 확장(주1회 SOOP stationinfo 16인 조회 →
  `/memberstats.json` PUT, §5-1 SA 인증 재사용) → member 상세·모달이 fetch, 실패 시 현행 placeholder 폴백.
  - 합격: 실 팔로워/방송시간 표기 + status cron(5분)과 독립 동작 + 무토큰 PUT 401.
- **E-3. LIVE "지금 방송 중" 그리드 재도입** (조건부): 과거 홈에 넣었다 사용자 요청으로 제거한 이력(2026-06-29) —
  **사용자 재요청 시에만**. 재구현 시 홈이 아닌 news/멀티뷰 상단 등 위치 재검토, `/status.json` 재사용이라 반나절.
- **E-4. 태그 자동완성 + 동일 URL 경고** (§7 리스크 "태그 오타"·§8-3 #2 "수동 중복 등록" 완화): 클립/아카이브 폼 태그
  입력에 기존 태그 datalist 제안(`D.list` 결과에서 태그 수집) + **클립 폼 제출 전 로드된 목록에 같은 url 존재 시
  "이미 등록된 클립입니다 — 그래도 등록할까요?" confirm 1줄**(이관 버튼의 URL 멱등 로직 재사용). 소품 — E-1/2 하는 김에.
- **E-5. 히어로 스트립 LIVE 실판별** → **§2.6-1로 앞당김 후보 승격**. 미착수 시 여기 잔존.
- **E-6. 최종 critique(§2.6-8, 07-13) P2 이하 백로그** — 전부 비긴급, 수요/콘텐츠 확보 시:
  - [P2] 홈 서비스 카드 5장(01~05) 템플릿감 — 실제 크루 자산(방송 스샷·굿즈·채팅 캡처)을 카드 배경으로 교체. 유일한 AI-문법 지적점.
  - [P3] 인트로 스킵 버튼 크기 상향(13px→15px 내외) / 핀 진행바 가시성(굵기·대비) 검토.
  - [P3] 멤버 상세 이전/다음 내비에 정렬 기준 표기.
  - [P3] pages CRUD 목록 `불러오기 실패: err.message` 노출 → stats처럼 고정 안내문 순화(§2.6-4 잔여).
  - [P3] 빈 상태 카피 통일("아직 등록된"/"등록된") / stats 승패 팔레트 정합화 검토(dataviz 상태색 규칙과 상충 주의).
  - (기존 §5-3 중복 지적 재확인) 헬프/온보딩 H10=1점·aria-live·검색/정렬.
- **E-7. 목록 페이지네이션(limitToLast)** (Claude, ~반나절) — §8-5 #3 성장 대응 1탄.
  - **착수 트리거(둘 중 먼저)**: clips 300건 초과 **또는** news 페이지 payload 150KB 초과(F-6 월점검에서 측정). 그 전엔 YAGNI.
  - 절차: ①규칙에 `.indexOn: ["createdAt"]`(clips/notices/schedules — 없으면 쿼리가 전체스캔 경고+거부) 게시
    ②`D.list(col, n)`에 `orderBy="createdAt"&limitToLast=n` 옵션 추가(기본 200, 무인자 호출은 현행 유지 = 하위호환)
    ③다량 소비 페이지부터 적용: news(클립5·일정5만 쓰므로 limitToLast=30이면 충분), clips 목록(200건+"더 보기"로 전량).
  - 합격: news payload가 데이터 총량과 무관하게 상수화(<30KB), 클립 목록 렌더 회귀 없음, 규칙 게시 후 콘솔 인덱스 경고 0.
- **E-8. 목록 캐시(TTL)** (Claude, ~1h) — 성장 대응 2탄, E-7보다 먼저 해도 됨(더 쌈).
  - **착수 트리거**: F-6 월점검에서 RTDB 다운로드 사용량 20% 초과.
  - 절차: `D.list`의 `?v=Date.now()` 캐시버스터 제거(RTDB REST는 어차피 no-cache 응답 — 버스터는 중복 안전장치일 뿐) +
    sessionStorage에 `{col, ts, data}` 60초 TTL 캐시(같은 세션에서 페이지 이동 시 재다운로드 생략, 쓰기 성공 시 해당 col 캐시 무효화).
  - 합격: 한 세션에서 clips→clip→clips 왕복 시 네트워크 fetch 1회, 글 저장 직후엔 새 데이터 즉시 반영(캐시 무효화 동작).
- **E-9. 동시편집 충돌 감지(낙관적 잠금)** (Claude, ~2h) — §8-3 #1 last-write-wins 해소.
  - **착수 트리거**: 실편집자(권한 계정) 5인 이상 활동 **또는** 덮어쓰기 사고 1회 발생 시. 16인 크루 현 규모에선 보류가 합리.
  - 절차(경량판 — ETag 대신 updatedAt 비교): 편집 모달 열 때 항목의 `updatedAt` 보관 → 저장 직전 단건 GET
    (`/{col}/{id}/updatedAt.json`, ~15B)으로 재확인 → 불일치 시 "다른 사용자가 방금 수정했습니다. 새로고침 후 다시 시도"
    confirm. (정식판은 RTDB REST `X-Firebase-ETag`/`if-match` 412 — 경량판으로 부족하면 승격.)
  - 합격: 탭 2개로 같은 공지 동시 수정 → 늦은 쪽에 경고 노출, 단독 수정은 마찰 없음.

### 5-5. 운영 위생 (Phase F — v3.2 실행 명세, 상시)
- **F-1. RTDB 주간 백업 자동화** (Claude 코드 + 사용자 워커 배포, ~2h): 워커 scheduled에 주1회 분기 추가 →
  `GET /.json`(§5-1 SA access_token 재사용) → **Cloudflare R2 put 권장**(GitHub 커밋안은 토큰 관리 부담이 커서 차선).
  - 합격: R2 버킷에 주1회 `backup-YYYY-MM-DD.json` 적재, 파일 열어 최상위 키 확인. 보존 8주 롤링.
- **F-2. 서비스계정 키 로테이션**(절차 §1-1): **Q6 최종 착지점** — §2.6-10 재상신이 거절되면 여기서 D+2주 내 1회 수행 권장.
  이후 연 1회(다음 2027-07). 노출키(§1-1)가 살아있는 동안 이 항목이 §7 최고 잠재영향 리스크임을 유지 기록.
- **F-3. `/rework` → 정식 경로 개명** (원하면, 저순위): SA로 데이터 복사 → `site.js REWORK_BASE` 1줄 → 규칙 이동 →
  구경로 동결. 실익 = 경로 미관뿐이라 무기한 보류 가능.
- **F-4. Lighthouse 분기 점검**: §2.6-7 기준선 대비 회귀 감시(성능/접근성/SEO ≥ 90 목표). 분기 1회, 이미지·스크립트
  추가가 있었던 분기엔 필수.
- **F-5. 문서 위생**: Phase 완료 시마다 이 문서 체크박스·§0 스냅샷 갱신 + 메모리 동기화. 레포 README 갱신,
  레포명 `Test_version` 개명 검토(§4-8과 동일 건 — Vercel Git 연결 재확인 필요라 안정기에).
- **F-6. 무료쿼터 월간 점검** (사용자 5분 + Claude 대조, 월 1회 — §8-5 #5 해소): 소진 시 알림 없이 503이 나므로 선제 확인.
  - 체크리스트(월초 1회): ①Firebase 콘솔 → 사용량 및 결제 → RTDB **다운로드 GB·저장 MB** 눈금 확인
    ②Vercel 대시보드 → Usage(대역폭)·Analytics(이벤트 수) ③Cloudflare → Workers 요청수.
  - Claude 대조(같은 날): `curl .../rework.json?shallow=true` + 컬렉션별 `wc -c`로 payload 성장 측정 →
    §8-1 표 갱신. **E-7 트리거(clips>300 or news>150KB)·E-8 트리거(다운로드>20%) 도달 여부 판정**이 이 점검의 본목적.
  - 경보선: 어느 축이든 월 사용량 50% 도달 → 해당 E 항목 즉시 착수 + 유료플랜 견적(§8-4 순서: Analytics→RTDB→Vercel).

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
| Q7 | `/rework` 쓰기를 계속 "임의 SOOP 계정" 개방 유지? | ①**현행 유지+C+ 상한(권장)** — 커뮤니티 기여 취지 보존, validate로 폭주만 차단 ②editor+ 제한 — 스팸 원천 차단이나 기여 문턱 상승. C+ 게시 때 함께 결정하면 규칙 1회 게시로 끝 | §5-2 | 신규(v4.0) |

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
| OneDrive 동기화 충돌(레포가 OneDrive 안) | 중 | 파일 잠김/유실 | 대량 산출물 금지, 커밋·푸시로 GitHub가 원본. **실제 발생(07-18 og 7종 삭제 발견 → 복원, §0-6)** |
| 익명 대량쓰기로 무료쿼터 고갈(운영 4경로 `.write:true`) | 저(표적 필요) | 사이트 503·데이터 훼손 | **Phase C(§5-1)** — cutover 후 즉시 잠금이 유일 해소. 그전엔 운영본 구조상 불가피(기존과 동일 노출) |
| 인증 사용자 스팸(크기·개수 상한 없음) | 저 | payload 비대·쿼터 소모 | **Phase C+(§5-2) validate 3중 상한** + admin 일괄삭제(D-1) + Q7 결정 |
| 데이터 누적×트래픽 성장으로 RTDB 다운로드 한계(§8-2: 트래픽 10배×3년치에서 도달) | 중(장기) | 월말 읽기 503 | **F-6 월점검**으로 조기 감지 → E-8(캐시)·E-7(limitToLast) 트리거 발동 |
| 동시편집 덮어쓰기(last-write-wins) | 저(현 규모) | 편집 유실(단건) | 4폼 더블클릭 가드 완료 + **E-9**(편집자 5인+ 시) |

---

## 8. 용량·부하·무료플랜 검수 (v4.0 신설 — 2026-07-18 실측 기반)

> 기준선: Vercel Analytics 최근 30일 = **방문자 1,591 / 3,104 PV**(일 ~103PV, 피크일 ~110명).
> 방법: RTDB 전 컬렉션 curl 실측 + 페이지별 fetch 호출 전수 grep + 무료플랜 공식 한도 대조.
> 결론 요약: **현행 무료 플랜 조합(Firebase Spark + Cloudflare Workers Free + Vercel Hobby)으로 전부 커버되고,
> 모든 축에서 여유 20배 이상.** 유일한 실질 리스크는 용량이 아니라 ①무인증 공개쓰기 경로(Phase C가 용량 관점에서도 1순위)
> ②인증 사용자 스팸 상한 부재(C+에서 validate로 차단) ③2~3년 후 `D.list` 전량 다운로드 비대화(E-7~8, 트리거 기반).

### 8-1. 읽기 경로 실측 — 페이지뷰 1회가 내려받는 양

RTDB 컬렉션 실측(2026-07-18 curl):

| 노드 | 크기 | 건수 | 건당 |
|---|---|---|---|
| `/status` | 3.9KB | 16인 | — (워커 5분 PUT) |
| `/contests`(운영) | 12.3KB | 15 | ~820B |
| `/rework/contests` | 13.3KB | 15 | ~886B |
| `/schedules`(운영, 이관취소로 미사용 예정) | 7.8KB | 73 | ~107B |
| `/crews` | 1.3KB | — | — |
| `/rework/notices` | 0.2KB | 1(테스트) | ~221B |
| `/rework/clips`·`/rework/schedules` | 0 | 0 | 추정 클립 ~350B·일정 ~250B |

페이지별 런타임 fetch(전수 grep — `D.list`는 **컬렉션 전량** 다운로드, `?v=Date.now()` 캐시버스터로 캐시 무효):

| 페이지 | fetch | 현재 payload | 1년 후 추정* |
|---|---|---|---|
| index·members·member | `/status` ×1 | 3.9KB | 3.9KB (고정) |
| multiview·members | `/status` + **5분 폴링**(setInterval 300s) | 3.9KB/5분 | 동일 |
| clips | clips ×1 | ~0 | ~80KB |
| news | notices+clips+schedules ×3 | ~0 | **~210KB (최대 페이지)** |
| schedule(-detail) | schedules ×1 | ~0 | ~100KB |
| archive | contests ×1 | 13KB | ~35KB |
| archive-detail | contests+clips ×2 | 13KB | ~115KB |
| stats | contests+crews | 15KB | ~36KB |
| notices/notice | notices ×1 | 0.2KB | ~25KB |

\* 1년 성장 가정(활발 운영 시나리오): 클립 주5건=연260건(80KB) · 일정 주10건=연520건(104KB) · 공지 월4건(25KB) · 아카이브 월2건(+21KB).
**연간 텍스트 총증가 ≈ 250KB** — RTDB 저장 1GB의 0.025%/년. 저장은 영원히 문제 아님(스팸 제외, §8-4).

### 8-2. 월간 쿼터 소모 계산 (RTDB 다운로드 10GB/월 대비)

- **현재(데이터 거의 빈 상태)**: 3,104PV × 평균 ~8KB ≈ **25MB/월 = 쿼터의 0.25%**.
- **1년 후 데이터 + 현 트래픽**: 3,104PV × 평균 ~60KB(status 페이지 4KB~news 210KB 가중) ≈ 190MB
  + 방치 탭 폴링(멀티뷰/멤버스 상시 10탭 가정: 10×288회×3.9KB=11MB/일) ≈ 340MB → **합 ~0.5GB/월 = 5%**.
- **한계선 공식**: `월PV × 평균payload ≈ 10GB`가 소진점.
  - 평균 100KB(1.5년치 데이터) → 월 10만PV(현재의 **32배**)에서 도달.
  - 평균 300KB(3년치 방치) → 월 3.3만PV(현재의 **10배**)에서 도달.
  - → **"트래픽 10배 × 데이터 3년치"가 교차하는 지점이 첫 벽.** 그전에 E-8(캐시)로 절반 감축, E-7(limitToLast)로 payload 상한 고정 가능 — 둘 다 트리거 조건 명시(§5-4).
- 운영 `/schedules` 7.8KB는 cutover 후 아무 페이지도 안 읽음(참고: 과거 73건은 Phase C에서 write 잠글 때 그대로 동결).

### 8-3. 50인 동시 수정 시나리오 (사용자 질문 직접 답변)

시나리오: 방송 이벤트 직후 **50명이 동시에** 클립 등록/수정(1년 후 데이터 규모 기준).

| 축 | 부하 | 한도 | 판정 |
|---|---|---|---|
| RTDB 읽기 | 50인 × (목록 로드+저장 후 재로드) ≈ 100 read × 80KB = **8MB** | 월 10GB의 0.08% | 무시 가능 |
| RTDB 쓰기 | 50 POST × ~0.4KB = 20KB, 수 초간 요청 ~150건 | RTDB는 초당 1,000건급 쓰기 처리 | 여유 수백 배 |
| 동시접속 100 제한 | **해당 없음** — REST 요청은 동시접속 카운트에 미집계(SDK 웹소켓 전용) | — | 구조적으로 면제 |
| 워커(50인 동시 로그인) | 3req/인 × 50 = 150req burst, RS256 서명 ~2ms CPU | 10만req/일·10ms CPU | <0.2% |
| identitytoolkit 교환 | 커스텀토큰 로그인 50건 | 무료·무제한 | 문제없음 |
| push 키 충돌 | 없음 — Firebase push 키는 충돌 방지 설계 | — | 안전 |

**인프라는 50인 동시가 아니라 500인 동시도 견딤. 진짜 리스크는 용량이 아니라 정합성 3종**:
1. **동일 항목 동시 PATCH = last-write-wins** (조용한 덮어쓰기, §2.5-1에서 기감지) → E-9(ETag 낙관적 잠금)로 해소, 트리거 기반.
2. **수동 중복 등록** — 50명이 같은 클립 URL 등록 시 서버 dedup 없음(이관 버튼만 URL 멱등). 실피해 = 목록 중복 노출뿐. → E-4 태그 자동완성 시 "동일 URL 경고" 1줄 동봉(§5-4 명시).
3. **더블클릭 중복** — 이미 4폼 가드 완료(07-11). 잔여 없음.

### 8-4. 무료플랜 전수 판정표

| 서비스·플랜 | 한도 | 현재 사용 | 1년 후 추정 | 판정 |
|---|---|---|---|---|
| **Firebase RTDB Spark** 저장 | 1GB | ~39KB (0.004%) | ~290KB | ✅ 사실상 무한 |
| **RTDB Spark** 다운로드 | 10GB/월 | ~25MB (0.25%) | ~0.5GB (5%) | ✅ 여유 20배 |
| **RTDB Spark** 동시접속 | 100 | REST라 미집계 | 동일 | ✅ 구조적 면제 |
| **Firebase Auth** | 커스텀토큰 무료 | 미미 | 미미 | ✅ |
| **Cloudflare Workers Free** | 10만req/일·10ms CPU | cron 288 + 로그인 수십 (<1%) | <2% | ✅ |
| **Vercel Hobby** 대역폭 | 100GB/월 | ~3GB 추정(초방문 1.9MB×1,591) | ~5GB | ✅ 정적+CDN이라 튼튼 |
| **Vercel Hobby** 성격 | 비상업 한정 | 팬사이트·비영리 | 동일 | ✅ 약관 적합 |
| **Vercel Analytics Hobby** | 5만 이벤트/월 | 3.1천 (6%) | ~10% | ✅ |

**유료 전환이 필요해지는 순서 예측**: ①Analytics(트래픽 16배) → ②RTDB 다운로드(10~30배, E-7/8로 지연 가능) → ③Vercel 대역폭(20배+). 어느 것도 단기 위험 아님.

### 8-5. 용량 관점 취약점 우선순위 (→ §5 배치)

| # | 취약점 | 공격/사고 시나리오 | 배치 |
|---|---|---|---|
| 1 | 운영 4경로 `.write:true` (무인증) | 익명 스크립트가 `/contests`에 1MB×1,000 PUT → 저장 1GB 소진 + 페이지 payload 폭탄(다운로드 쿼터 고갈) + 데이터 삭제 가능 | **Phase C (§5-1) — 이미 1순위, 용량 근거 추가** |
| 2 | `/rework` 쓰기 = 임의 SOOP 계정 허용·필드/크기 상한 없음 | 가입만 한 악성 사용자가 대형 문자열 대량 create → 같은 폭탄(단, 인증 흔적 남음) | **Phase C+ (§5-2) — validate 상한 상세화** |
| 3 | `D.list` 전량 다운로드 + 캐시버스터 | 악의 없어도 데이터 누적 × 트래픽 성장의 곱으로 쿼터 접근 | **E-7·E-8 (트리거 기반)** |
| 4 | 동시편집 last-write-wins | 50인 동시 수정 시 덮어쓰기 | **E-9 (트리거 기반)** |
| 5 | 쿼터 무감시 | 소진돼도 알림 없이 503 | **F-6 (월 1회 확인 루틴)** |

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
  └─ 소스: 03_WCHP/whale-auth-worker/worker.js (레포 밖 — 배포는 대시보드 붙여넣기)

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
games{game_NNN:{name,result:bool(true=승)}}, members[명], opponents[{crewId,name,result:bool **true=승**(운영 admin.js isWin 규약, 07-11 실데이터 15건 교차검증 — 이전 "true=패(반전)" 기록은 오독이었고 렌더 버그까지 유발해 07-11 수정)}],
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
- `python3 src/build.py` → 19페이지 생성 성공(07-11 stats 추가로 18→19).
- 전 페이지 인라인 `<script>` `new Function` 파싱 0 에러(38개).
- 시드 버튼: clips/schedule/notices=0(⚠️clips의 "운영 아카이브에서 클립 불러오기"는 §2.5-4 이관 버튼 — 시드 아님, 유지), archive=유지. 죽은 `WHALE_*` 주입 0(⚠️member/members의 `WHALE_MEMBERS`·multiview의 `WHALE_META`는 members.json 빌드타임 실렌더용 — 정상, 검사 대상 아님).
- 멤버 페이지에 옛 placeholder 부서(영업부/기획실 등) 0.
- 클립 폼 `tags`, 아카이브 폼 `tags`+`category` 존재. 칩 `data-f`=all/크루대전/컨텐츠.

## 부록 D. 명령어 치트시트

```bash
# 빌드(19페이지 재생성 — pages/ 직접 수정 금지. 빌드 후 커밋에 pages/ 포함 확인!)
python3 src/build.py
# 로컬 미리보기 (리워크 루트) — 화면 안 바뀌면 Ctrl+Shift+R
python3 -m http.server 8792
# 푸시 (로컬 브랜치 main, origin/main 추적 — 1-3 완료)
git push
# 워커 신규 엔드포인트 생존 확인 (401/400이면 정상)
curl -s -o /dev/null -w "%{http_code}" -X POST https://whale-status-worker.kyefyx.workers.dev/auth/firebase
# RTDB 컬렉션 건수 훑기
curl -s "https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/rework.json?shallow=true"
# embedUrlOf 보안 재검증(부록 C-2) / 규칙 매트릭스(부록 C-1)
#   → "임베드 보안 테스트 돌려줘" / "검증 매트릭스 다시 돌려줘"
```
