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
    console.log('✅ 클립 검색 8 · 아카이브 필터 11 · 아카이브→클립 연결 6 · 홈 정렬 5 · 조회수 5 — 전부 통과');
  };
  process.on('exit', () => { if (pending) { console.error('❌ 조회수 검사가 끝나지 않음'); process.exitCode = 1; } });
}
