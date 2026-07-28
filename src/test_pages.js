/* 빌드 산출물 자체 점검 — 클립 검색 / 아카이브 필터 / 아카이브→클립 연결 / 홈 베스트 클립 정렬.
   각 로직을 복붙하지 않고 index.html·pages/*.html에 실제로 박힌 코드를 꺼내 실행하므로,
   build.py에서 로직이 바뀌면 여기가 같이 따라가거나 '찾지 못함'으로 즉시 깨진다.
   실행: node src/test_pages.js   (python3 src/build.py 이후)
   eval 근거: 외부 입력이 아니라 이 저장소가 방금 만든 자기 코드. 로컬 개발 전용, 배포되지 않는다. */
const fs = require('fs');
const read = p => fs.readFileSync(__dirname + '/../' + p, 'utf8');
const grab = (src, re, what) => {
  const m = re.exec(src);
  if (!m) throw new Error(`${what}를 찾지 못함 — 빌드했는지, 코드가 바뀌었는지 확인`);
  return m;
};
let fail = 0;
const ok = (cond, msg) => { if (!cond) { fail++; console.error('  ✗ ' + msg); } };

/* ── 1. 클립 검색 (pages/clips.html) ───────────────────────────── */
{
  const page = read('pages/clips.html');
  let query = '';
  eval(grab(page, /function hay\(c\)\{[\s\S]*?\n  \}\n  function matches\(c\)\{[\s\S]*?\n  \}/, '클립 hay/matches')[0]);

  const C = [
    { title: '크루대전 하이라이트', creator: '고래상사', category: '대회', desc: '결승전', tags: ['크루대전', '여름특집'] },
    { title: '마렌 폭주 모음', creator: '김마렌', category: '게임', desc: '', tags: [] },
  ];
  const hit = q => { query = q; return C.filter(matches).length; };
  ok(hit('') === 2, '빈 검색어 = 전체');
  ok(hit('크루대전') === 1, '제목/태그 일치');
  ok(hit('김마렌') === 1, '제작자 일치');
  ok(hit('결승') === 1, '설명 일치');
  ok(hit('대회') === 1, '카테고리 일치');
  ok(hit('크루대전 여름') === 1, '공백 = AND (둘 다 있음)');
  ok(hit('크루대전 김마렌') === 0, '공백 = AND (교집합 없음)');
  ok(hit('마렌') === 1, '부분 일치');
}

/* ── 2. 아카이브 필터 (pages/archive.html) ─────────────────────── */
{
  const page = read('pages/archive.html');
  let filt = 'all', query = '', fMem = '', fGame = '', fWin = '';
  // '기타'는 명단(RSET)·상위 게임(topGames) 밖을 뜻한다 — 페이지에선 fillOptions가 채우는 값
  const ETC = '기타';
  const RSET = { 울산큰고래: 1, 김마렌: 1, 견자희: 1 };   // 현재 멤버, 쏭이는 졸업했다고 가정
  let topGames = { '리그 오브 레전드': 1, 철권: 1 };      // 테트리스는 3회 미만이라 제외됐다고 가정
  eval(grab(page, /function gameNames\(c\)\{[\s\S]*?\n  \}\n  \/\* 직접입력[\s\S]*?function matches\(c\)\{[\s\S]*?\n  \}/, '아카이브 matches')[0]);

  const A = [
    { title: '고래상사 vs 습레기통 롤 크루대전', date: '2025-10-15', rank: 1,
      members: ['울산큰고래', '김마렌'], games: { g1: { name: '리그 오브 레전드' } },
      opponents: [{ name: '습레기통' }] },
    { title: '종겜올림픽', date: '2026-03-02', rank: 5,
      members: ['견자희', '쏭이'], games: { g1: { name: '철권' }, g2: { name: '테트리스' } },
      opponents: [{ name: '버인협회' }] },
  ];
  const run = () => A.filter(matches).map(c => c.title);
  const reset = () => { filt = 'all'; query = ''; fMem = ''; fGame = ''; fWin = ''; };

  ok(run().length === 2, '기본 = 전체');
  reset(); fMem = '김마렌';
  ok(run().join() === A[0].title, '참여 멤버 필터');
  reset(); fGame = '철권';
  ok(run().join() === '종겜올림픽', '게임 필터');
  reset(); fWin = 'win';
  ok(run().join() === A[0].title, '우승만');
  reset(); fWin = 'other';
  ok(run().join() === '종겜올림픽', '우승 외');
  reset(); query = '습레기통';
  ok(run().join() === A[0].title, '직접입력 — 상대 크루');
  reset(); query = '테트리스';
  ok(run().join() === '종겜올림픽', '직접입력 — 게임 이름');
  reset(); query = '견자희';
  ok(run().join() === '종겜올림픽', '직접입력 — 참여 멤버');
  reset(); query = '롤 크루대전';
  ok(run().join() === A[0].title, '직접입력 — 공백 AND');
  reset(); fMem = '김마렌'; fWin = 'other';
  ok(run().length === 0, '조건 조합 = 교집합');
  reset(); fMem = '울산큰고래'; fGame = '리그 오브 레전드'; fWin = 'win'; query = '습레기통';
  ok(run().join() === A[0].title, '네 조건 동시 만족');
  reset(); fMem = ETC;
  ok(run().join() === '종겜올림픽', '멤버 기타 = 현재 명단 밖(쏭이)이 낀 기록');
  reset(); fGame = ETC;
  ok(run().join() === '종겜올림픽', '게임 기타 = 상위 목록 밖(테트리스)이 낀 기록');
  reset(); fMem = ETC; fGame = '철권';
  ok(run().join() === '종겜올림픽', '기타도 다른 조건과 교집합');

  // 선택지 목록 자체 — 명단 필터·3회 임계·기타 접기가 실제로 걸리는지
  {
    const ROSTER = ['울산큰고래', '김마렌', '견자희'], GAME_MIN = 3;
    let all = [], memOpts = [], gameOpts = [];
    const memEl = {}, gameEl = {};
    const fillSelect = (sel, list) => { (sel === memEl ? memOpts : gameOpts).length = 0; (sel === memEl ? memOpts : gameOpts).push(...list); };
    eval(grab(page, /  function fillOptions\(\)\{[\s\S]*?\n  \}/, 'fillOptions')[0]);
    const rec = (members, games) => ({ members, games: games.reduce((o, n, i) => (o['g' + i] = { name: n }, o), {}) });
    all = [
      rec(['울산큰고래', '쏭이'], ['롤', '롤']),        // 같은 기록 안 중복도 각각 센다
      rec(['김마렌'], ['롤', '철권']),
      rec(['김마렌'], ['롤']),
    ];
    fMem = ''; fGame = '';
    fillOptions();
    ok(memOpts.join() === '울산큰고래,김마렌,기타', '멤버 = 명단 순서, 등장 안 한 견자희 제외, 졸업생은 기타');
    ok(gameOpts.join() === '롤,기타', '게임 = 3회 이상만, 나머지는 기타 한 칸');
    ok(topGames['롤'] === 1 && !topGames['철권'], 'topGames가 matches의 기타 판정 기준으로 갱신됨');
  }
}

/* ── 3. 아카이브 → 클립 '보러가기' (pages/archive-detail.html) ── */
{
  const det = read('pages/archive-detail.html');
  let allClips = [], cur = null, rel = [];
  // tagsOf는 한 줄 함수 → 블록 종료로 안 잡힌다. keywordsOf까지 한 덩어리로.
  eval(grab(det, /function tagsOf\(x\)\{.*?\}\n[\s\S]*?function relatedOf\(contest\)\{[\s\S]*?\n  \}/, 'relatedOf')[0]);

  // 운영 실데이터 모양: 기록에는 tags가 없고, 클립 tags에 대회 제목이 들어 있다
  allClips = [
    { id: 'a', title: '러스트 엉망7창 서버 클립 1', tags: ['러스트 엉망7창 서버'] },
    { id: 'b', title: '러스트 엉망7창 서버 클립 2', tags: ['러스트 엉망7창 서버'] },
    { id: 'c', title: '감징어게임 클립', tags: ['감징어게임'] },
  ];
  cur = { title: '러스트 엉망7창 서버' };
  rel = relatedOf(cur);
  ok(rel.map(c => c.id).join() === 'a,b', 'tags 없는 기록도 제목으로 클립과 묶인다');
  ok(relatedOf({ title: '없는 대회' }).length === 0, '엉뚱한 기록은 0건');
  ok(relatedOf({ title: '크루 골든벨', tags: ['크루 골든벨'] }).length === 0, 'tags가 있어도 오작동 없음');

  // 링크가 넘기는 태그 고르는 로직을 그대로 실행
  eval(grab(det, /var kw=keywordsOf\(cur\)[\s\S]*?\n    \}\);/, '보러가기 태그 선택')[0]);
  ok(t0 === '러스트 엉망7창 서버', '실제로 클립을 묶고 있는 태그를 넘긴다');
  // clips.html?t= 는 태그 정확일치로 거른다 → 관련 클립과 같은 집합이어야 한다
  const opened = allClips.filter(c => (c.tags || []).indexOf(t0) >= 0).map(c => c.id);
  ok(opened.join() === rel.map(c => c.id).join(), '보러가기 결과 = 관련 클립과 동일 집합');

  // 태그와 제목이 어긋난 기록에서도 죽은 링크가 되지 않아야 한다
  cur = { title: '감징어게임', tags: ['존재하지않는태그'] };
  rel = relatedOf(cur);
  eval(grab(det, /var kw=keywordsOf\(cur\)[\s\S]*?\n    \}\);/, '보러가기 태그 선택')[0]);
  ok(t0 === '감징어게임', '첫 키워드가 아니라 실제로 묶인 키워드를 넘긴다');
}

/* ── 3-b. 클립 → 아카이브 역방향 (pages/clip.html) ────────────── */
{
  const page = read('pages/clip.html');
  let allContests = [];
  eval(grab(page, /  function tagsOf\(x\)\{[\s\S]*?\n  function linksTo\(contest,clip\)\{[\s\S]*?\n  \}/, 'linksTo')[0]);
  eval(grab(page, /  function contestsOf\(clip\)\{[\s\S]*?\n  \}/, 'contestsOf')[0]);

  allContests = [
    { id: 'c1', title: '러스트 엉망7창 서버' },              // 태그 없음 = 운영 실데이터 모양
    { id: 'c2', title: '감징어게임', tags: ['감징어게임'] },
  ];
  ok(contestsOf({ tags: ['러스트 엉망7창 서버'] }).map(c => c.id).join() === 'c1', '기록 제목 태그로 역방향 연결');
  ok(contestsOf({ tags: ['감징어게임'] }).map(c => c.id).join() === 'c2', 'tags 있는 기록도 역방향 연결');
  ok(contestsOf({ tags: [] }).length === 0, '태그 없는 클립은 0건');
  ok(contestsOf({ tags: ['없는대회'] }).length === 0, '엉뚱한 태그는 0건');
  // 양방향 대칭 — 상세 두 페이지가 같은 판정(linksTo)을 쓰는지가 핵심
  const clip = { id: 'x', tags: ['감징어게임'] };
  ok(contestsOf(clip).length === 1 && linksTo(allContests[1], clip), '기록→클립과 클립→기록이 같은 판정');
}

/* ── 3-c. 클립 태그 콤보박스 상태 (pages/clips.html) ──────────── */
{
  const page = read('pages/clips.html');
  const chipHtml = { innerHTML: '' };
  const clTagChips = chipHtml, clForm = { tags: { value: '' } };
  const esc = s => String(s);
  let clTags = [];
  eval(grab(page, /  function clSyncTags\(\)\{[\s\S]*?\n  function clAddTag\(t\)\{[\s\S]*?\n  \}/, '태그 상태 헬퍼')[0]);
  eval(grab(page, /  function clHasTag\(n\)\{.*\}/, 'clHasTag')[0]);

  clSetTags(['크루대전']);
  clAddTag('여름특집');
  ok(clForm.tags.value === '크루대전, 여름특집', '선택한 태그가 저장 형식(쉼표 문자열)으로 반영');
  clAddTag('  여름특집  ');
  clAddTag('여름특집'.toUpperCase());
  ok(clTags.length === 2, '공백·대소문자만 다른 중복은 추가되지 않음');
  clAddTag('   ');
  ok(clTags.length === 2, '빈 입력은 무시');
  ok(clHasTag('크루대전') && !clHasTag('없는태그'), 'clHasTag = 후보 목록에서 이미 고른 것 거르는 기준');
  clSetTags([]);
  ok(clForm.tags.value === '' && chipHtml.innerHTML === '', '새 글 열 때 태그가 비워짐');
}

/* ── 4. 홈 베스트 클립 정렬 (index.html) ──────────────────────── */
{
  const home = read('index.html');
  const cmp = eval('(' + grab(home, /list\.sort\((function \(a, b\) \{[\s\S]*?\n        \})\);/, '홈 클립 정렬')[1] + ')');
  const pick = arr => arr.slice().sort(cmp).map(c => c.t);

  ok(pick([{ t: 'hi-views', views: 9999, createdAt: 5 }, { t: 'feat', featured: true, views: 0, createdAt: 1 }])[0] === 'feat',
    '대표 클립이 최우선');
  ok(pick([{ t: 'f1', featured: true, views: 10 }, { t: 'f2', featured: true, views: 50 }, { t: 'n1', views: 999 }])
    .join() === 'f2,f1,n1', '대표끼리는 조회수 순, 그다음 일반');
  ok(pick([{ t: 'a', views: 3 }, { t: 'b', views: 30 }, { t: 'c', views: 300 }]).join() === 'c,b,a', '조회수 내림차순');
  ok(pick([{ t: 'old', createdAt: 100 }, { t: 'new', createdAt: 900 }, { t: 'mid', createdAt: 500 }])
    .join() === 'new,mid,old', 'views 없으면 최근 등록순(현재 데이터가 이 경우)');
  ok(pick([{ t: 'x', views: null, createdAt: 1 }, { t: 'y', views: '', createdAt: 2 }]).join() === 'y,x',
    'views null/빈값이어도 정렬이 깨지지 않음');
}

/* ── 4-b. 인사기록카드 D-day (assets/site.js + members.json) ──────
   기대값은 운영자의 '카운트다운 시트지'(2026-07-28 기준)를 그대로 옮긴 것.
   오늘 날짜를 그날로 고정해 우리 계산이 시트와 한 자리도 안 틀리는지 본다. */
{
  const src = read('assets/site.js');
  const RealDate = globalThis.Date;
  class FixedDate extends RealDate {          // 인자 없는 new Date() = 2026-07-28 (로컬 자정)
    constructor(...a) { super(...(a.length ? a : [2026, 6, 28])); }
  }
  FixedDate.UTC = RealDate.UTC;
  const Date = FixedDate;                     // eval된 코드가 이 Date를 본다
  eval(grab(src, /  var DAY = 86400000;[\s\S]*?\n  function setStat\(/, '인사기록카드 날짜 헬퍼')[0]
    .replace(/\n  function setStat\($/, ''));

  const members = JSON.parse(read('src/content/members.json')).members;
  const byName = Object.fromEntries(members.map(m => [m.name, m]));
  // 이름: [생일 D-, 데뷔 D+, 데뷔 경과, 입사 D+, 입사 경과]
  const SHEET = {
    울산큰고래: [279, 6072, '16년 7개월 16일', 324, '0년 10개월 21일'],
    견자희: [274, 5191, '14년 2개월 17일', 321, '0년 10개월 18일'],
    감자가비: [21, 3222, '8년 9개월 27일', 319, '0년 10개월 16일'],
    이지수: [254, 3134, '8년 7개월 0일', 319, '0년 10개월 16일'],
    쏭이: [335, 3132, '8년 6개월 28일', 319, '0년 10개월 16일'],
    밀크티냠: [13, 2482, '6년 9개월 17일', 319, '0년 10개월 16일'],
    묵아: [235, 2264, '6년 2개월 12일', 54, '0년 1개월 24일'],
    김마렌: [310, 2034, '5년 6개월 27일', 319, '0년 10개월 16일'],
    멜로딩딩: [37, 1983, '5년 5개월 7일', 324, '0년 10개월 21일'],
    셀키: [209, 905, '2년 5개월 24일', 51, '0년 1개월 21일'],
    희희덕: [278, 887, '2년 5개월 6일', 114, '0년 3개월 23일'],
    조아라: [211, 885, '2년 5개월 4일', 319, '0년 10개월 16일'],
    빡쏘: [65, 617, '1년 8개월 10일', 324, '0년 10개월 21일'],
    프하: [141, 542, '1년 5개월 27일', 54, '0년 1개월 24일'],
    삐요코: [308, 529, '1년 5개월 14일', 323, '0년 10개월 20일'],
    채하나: [164, 236, '0년 7개월 24일', 114, '0년 3개월 23일'],
  };
  ok(members.length === 16 && Object.keys(SHEET).every(n => byName[n]), '시트 16인 = members.json 16인');
  let diff = 0;
  Object.keys(SHEET).forEach(n => {
    const m = byName[n]; if (!m) return;
    const e = SHEET[n], b = birthInfo(m.birth), d = pastInfo(m.debut), j = pastInfo(m.joined);
    const got = [b && b.d, d && d.d, d && d.e, j && j.d, j && j.e].join('|');
    const want = ['D-' + e[0], 'D+' + e[1], e[2], 'D+' + e[3], e[4]].join('|');
    if (got !== want) { diff++; console.error(`  ✗ ${n}\n    기대 ${want}\n    실제 ${got}`); }
  });
  ok(diff === 0, `16인 D-day가 시트와 일치 (어긋난 인원 ${diff}명)`);
  // 경계: 오늘이 생일이면 D-365가 아니라 D-DAY
  ok(birthInfo('07-28').d === 'D-DAY', '당일 생일은 D-DAY');
  ok(birthInfo('07-29').d === 'D-1', '내일 생일은 D-1');
  ok(pastInfo('2026-07-28').d === 'D+0', '오늘 입사면 D+0');
  ok(birthInfo('') === null && pastInfo('2026-7-1') === null, '형식이 어긋나면 null(칸은 — 로 표시)');
  // 일수를 빌려오는 경로: 2024-02-29 → 2026-07-28 = 2년 4개월 + (6월 30일에서 빌린) 29일
  ok(pastInfo('2024-02-29').e === '2년 4개월 29일', '일(日)이 모자라면 직전 달 길이로 빌려온다');
  ok(pastInfo('2026-06-30').e === '0년 0개월 28일', '한 달 안이면 0년 0개월');
  // 홈은 site.js를 로드하지 않아 같은 코드를 인라인으로 들고 있다 — 사본이 어긋나면 홈만 조용히 틀린다
  const cut = s => grab(s, /  var DAY = 86400000;[\s\S]*?\n  function setStat\(/, '날짜 헬퍼')[0];
  ok(cut(read('index.html')) === cut(src), '홈 인라인 사본과 site.js 사본이 동일');
  // JS가 부르는 칸 이름과 마크업의 data-k가 어긋나면 카드가 조용히 빈칸이 된다
  const keys = [...src.matchAll(/setStat\('(\w+)'/g)].map(m => m[1]);
  ok(keys.join() === 'birth,debut,joined', 'site.js가 채우는 칸 3개');
  // 인사기록카드 모달은 홈에만 있다(하위 페이지는 member.html 상세로 이동)
  const home = read('index.html');
  ok(keys.every(k => home.includes(`data-k="${k}"`)), '홈 인사기록카드 칸 3개가 마크업에 존재');
  // 멤버 상세는 같은 계산(WhaleDate)을 빌려 쓴다 — 더미 스탯 잔재가 없어야 한다
  const det = read('pages/member.html');
  ok(/WhaleDate/.test(det) && /window\.WhaleDate = \{/.test(src), '멤버 상세가 site.js 날짜 계산을 공유');
  ['index.html', 'pages/member.html'].forEach(f => {
    const h = read(f);
    ok(!/mstat\d|누적 시청자|m\.stats/.test(h), `${f} 옛 더미 스탯 잔재 없음`);
  });
}

/* ── 4.5 개발용 로그인 가드 (assets/site.js + index.html 인라인 사본) ── */
{
  // 운영 도메인에 dev 로그인이 남으면 /permissions 닉 열거 + admin-only UI 게이팅이 우회된다
  const cut = s => grab(s, /  var DEV_LOGIN_OK = [\s\S]*?devLoginForm = null; \}/, '개발용 로그인 가드')[0];
  const guard = cut(read('assets/site.js'));
  ok(guard === cut(read('index.html')), '홈 인라인 사본과 site.js의 dev 로그인 가드가 동일');

  const removedOn = hostname => {
    let removed = false;
    const form = { closest: () => ({ remove: () => { removed = true; } }) };
    new Function('location', 'devLoginForm', guard)({ hostname }, form);
    return removed;
  };
  ok(removedOn('www.goraesangsa.com') === true, '운영 도메인에선 dev 로그인 마크업 제거');
  ok(removedOn('localhost') === false, 'localhost에선 유지');
  ok(removedOn('') === false, 'file:// 열람에선 유지');
}

/* ── 5. 사이트 조회수 WhaleViews (assets/site.js) ─────────────── */
{
  const src = grab(read('assets/site.js'),
    /window\.WhaleViews = \{[\s\S]*?\n  \};/, 'WhaleViews')[0];

  // 헬퍼가 기대는 주변 환경만 흉내 낸다 (site.js 안에서는 IIFE 지역변수)
  const REWORK_BASE = 'https://db.example/rework';
  const jfetch = url => calls.push(['GET', url]) && Promise.resolve(viewMap);
  const store = {};
  const sessionStorage = { getItem: k => store[k] || null, setItem: (k, v) => { store[k] = v; } };
  let calls = [], viewMap = {}, putBody = null;
  global.fetch = (url, opt) => {
    calls.push([opt && opt.method || 'GET', url]);
    if (opt && opt.method === 'PUT') { putBody = opt.body; return Promise.resolve({}); }
    return Promise.resolve({ json: () => Promise.resolve(viewMap.__n) });
  };
  const window = {};
  eval(src);
  const V = window.WhaleViews;

  // load(): 카운터 맵을 목록에 합류, 없는 건 0
  viewMap = { a: 12, b: 3 };
  const items = [{ id: 'a' }, { id: 'b' }, { id: 'c' }];
  V.load(items).then(() => {
    ok(items[0].views === 12 && items[1].views === 3, 'load — 카운터 값 합류');
    ok(items[2].views === 0, 'load — 카운터 없는 클립은 0');
  });

  // bump(): 현재값+1로 PUT
  viewMap.__n = 41;
  V.bump('a');
  setTimeout(() => {
    ok(putBody === '42', `bump — 현재값+1을 쓴다 (기대 42, 실제 ${putBody})`);
    // 같은 세션 재호출은 요청 자체가 나가지 않아야 한다
    const before = calls.length;
    V.bump('a');
    ok(calls.length === before, 'bump — 같은 세션 중복 차단');
    // 처음 보는 클립은 0+1
    putBody = null; viewMap.__n = null;
    V.bump('z');
    setTimeout(() => {
      ok(putBody === '1', `bump — 카운터 없던 클립은 1 (실제 ${putBody})`);
      done();
    }, 0);
  }, 0);
  var pending = true;
  var done = () => {
    pending = false;
    if (fail) { console.error(`\n❌ ${fail}건 실패`); process.exit(1); }
    console.log('✅ 클립 검색 8 · 아카이브 필터 17 · 아카이브↔클립 연결 11 · 태그 콤보박스 5 · 홈 정렬 5 · 인사기록카드 14 · dev 로그인 가드 4 · 조회수 5 — 전부 통과');
  };
  process.on('exit', () => { if (pending) { console.error('❌ 조회수 검사가 끝나지 않음'); process.exitCode = 1; } });
}
