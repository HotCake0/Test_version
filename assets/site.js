/* =========================================================
   고래상사 공유 스크립트 (site.js)
   모든 하위 페이지가 공유하는 크롬(header/GNB/로그인/리빌/스크롤탑/멤버모달).
   메인 홈(index.html)은 자체 인라인 스크립트를 사용하므로 이 파일을 쓰지 않는다.
   전 함수는 요소 존재를 가드해, 해당 마크업이 없는 페이지에서도 안전하다.
   ========================================================= */
(function () {
  'use strict';

  var PRM = matchMedia('(prefers-reduced-motion:reduce)').matches;
  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- 푸터 연도 ---- */
  var fyEl = document.getElementById('footerYear');
  if (fyEl) fyEl.textContent = new Date().getFullYear();

  /* ---- 헤더 scrolled ---- */
  var header = document.getElementById('header');
  if (header) {
    var chkHeader = function () { header.classList.toggle('scrolled', window.scrollY > 30); };
    window.addEventListener('scroll', chkHeader, { passive: true });
    chkHeader();
  }

  /* ---- GNB 우측 드로어 ---- */
  var hambBtn    = document.getElementById('hambBtn');
  var gnbOverlay = document.getElementById('gnbOverlay');
  var menuOpen   = false;
  function openGnb() {
    menuOpen = true;
    gnbOverlay.classList.add('active');
    gnbOverlay.setAttribute('aria-hidden', 'false');
    hambBtn.setAttribute('aria-expanded', 'true');
    hambBtn.setAttribute('aria-label', '메뉴 닫기');
    document.body.style.overflow = 'hidden';
    var f = $('.grp-t', gnbOverlay); if (f) f.focus();  /* 키보드/SR 사용자를 메뉴 안으로 */
  }
  function closeGnb() {
    menuOpen = false;
    gnbOverlay.classList.remove('active');
    gnbOverlay.setAttribute('aria-hidden', 'true');
    hambBtn.setAttribute('aria-expanded', 'false');
    hambBtn.setAttribute('aria-label', '메뉴 열기');
    document.body.style.overflow = '';
    if (gnbOverlay.contains(document.activeElement)) hambBtn.focus();  /* 포커스 복귀 */
    $$('.grp.open', gnbOverlay).forEach(function (g) {
      g.classList.remove('open');
      var t = $('.grp-t', g);
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  }
  if (hambBtn && gnbOverlay) {
    hambBtn.addEventListener('click', function () { menuOpen ? closeGnb() : openGnb(); });
    $$('a', gnbOverlay).forEach(function (a) { a.addEventListener('click', closeGnb); });
    /* 서브메뉴 탭/클릭 토글 — 터치·키보드 접근 (hover는 @media(hover:hover) 전용) */
    $$('.grp-t', gnbOverlay).forEach(function (t) {
      t.addEventListener('click', function () {
        var open = t.parentElement.classList.toggle('open');
        t.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ---- 로그인 모달 + 숲(SOOP) 권한 게이팅 (운영본과 동일 패턴) ---- */
  var loginBtn     = document.getElementById('loginBtn');
  var loginModalBg = document.getElementById('loginModalBg');
  var loginClose   = document.getElementById('loginClose');
  var loginMsg     = document.getElementById('loginMsg');
  var soopLoginBtn = document.getElementById('soopLoginBtn');
  var devLoginForm = document.getElementById('devLoginForm');

  var SOOP_CLIENT_ID = '936af2a8f0c73e188f1318c8dd6a2737';
  var SOOP_AUTH_URL  = 'https://openapi.sooplive.com/auth/code';
  var REDIRECT_URI   = location.origin + '/auth/callback.html';
  var FIREBASE_BASE  = 'https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app';
  // Firebase 웹 API 키(공개키, 노출 무방) — idToken 만료 시 refresh에 필요
  var FIREBASE_WEB_API_KEY = 'AIzaSyBZpdQES1EeZLieWiRwo-sNrA2wJQ6vZ9k';

  function currentUser() {
    try { return JSON.parse(sessionStorage.getItem('soop_user') || 'null'); }
    catch (e) { return null; }
  }
  function isAdmin(u)    { u = u || currentUser(); return !!(u && (u.role === 'admin' || u.role === 'editor')); }
  function isLoggedIn(u) { u = u || currentUser(); return !!(u && u.role); }
  // 이 항목을 지금 사용자가 수정/삭제할 수 있는가: 관리자이거나, 본인이 만든 것(soop id 일치).
  function canEdit(item) {
    var u = currentUser();
    if (!u) return false;
    if (isAdmin(u)) return true;
    return !!(item && item.ownerId != null && item.ownerId === u.id);
  }

  function applyRole() {
    var u = currentUser(), admin = isAdmin(u), inUser = isLoggedIn(u);
    $$('.admin-only').forEach(function (el) { el.classList.toggle('is-shown', admin); });   // 관리자 전용
    $$('.auth-only').forEach(function (el) { el.classList.toggle('is-shown', inUser); });    // 로그인 사용자 전용
    document.documentElement.classList.toggle('is-admin', admin);
    document.documentElement.classList.toggle('is-auth', inUser);
    if (!loginBtn) return;
    if (inUser) {
      loginBtn.textContent = (u.nickname || '사용자') + ' ⏏';
      loginBtn.classList.toggle('is-admin', admin);
      loginBtn.title = '로그아웃 (' + (u.role || '') + ')';
    } else {
      loginBtn.textContent = '로그인';
      loginBtn.classList.remove('is-admin');
      loginBtn.title = '';
    }
    // 로그인/로그아웃으로 권한이 바뀌면 목록 페이지가 버튼을 다시 그리도록 신호를 보낸다.
    try { document.dispatchEvent(new CustomEvent('whale:authchange')); } catch (e) {}
  }

  function soopLogin() {
    sessionStorage.setItem('soop_return', location.pathname + location.search);
    var p = new URLSearchParams({ response_type: 'code', client_id: SOOP_CLIENT_ID, redirect_uri: REDIRECT_URI });
    location.href = SOOP_AUTH_URL + '?' + p.toString();
  }
  function openLogin()  { if (loginModalBg) loginModalBg.hidden = false; }
  function closeLogin() { if (loginModalBg) loginModalBg.hidden = true; if (loginMsg) loginMsg.textContent = ''; }

  if (loginBtn) loginBtn.addEventListener('click', function () {
    if (isLoggedIn()) {
      sessionStorage.removeItem('soop_user');
      sessionStorage.removeItem('soop_fb');   // Firebase idToken도 함께 폐기
      applyRole(); return;
    }
    openLogin();
  });
  if (loginClose) loginClose.addEventListener('click', closeLogin);
  if (loginModalBg) loginModalBg.addEventListener('click', function (e) { if (e.target === loginModalBg) closeLogin(); });
  if (soopLoginBtn) soopLoginBtn.addEventListener('click', soopLogin);

  // 개발용 로그인: 실제 OAuth가 불가한 로컬에서 닉네임으로 세션을 흉내낸다.
  // 권한 계정이면 admin/editor, 아니면 member(로그인만 한 일반)로 세션 생성 → 일반 사용자 CRUD도 테스트 가능.
  // ⚠️로컬 전용 — 운영 도메인에선 마크업째 제거한다(/permissions 닉 열거 + admin-only UI 게이팅 우회 차단).
  //   같은 블록이 index.html 인라인 사본에도 있다(홈은 site.js 미로드) — 한쪽만 고치지 말 것.
  var DEV_LOGIN_OK = !location.hostname || /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  if (devLoginForm && !DEV_LOGIN_OK) { (devLoginForm.closest('details') || devLoginForm).remove(); devLoginForm = null; }
  if (devLoginForm) devLoginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var nick = devLoginForm.querySelector('[name="nick"]').value.trim();
    if (!nick) { loginMsg.textContent = '숲 닉네임을 입력하세요.'; return; }
    loginMsg.textContent = '권한 확인 중...';
    fetch(FIREBASE_BASE + '/permissions/' + encodeURIComponent(nick) + '.json')
      .then(function (r) { return r.json(); })
      .then(function (perm) {
        var role = (perm === 'admin' || perm === 'editor') ? perm : 'member';
        // 개발 세션은 실제 soop id가 없으므로 닉 기반 유사 id로 소유권 테스트가 되게 한다.
        sessionStorage.setItem('soop_user', JSON.stringify({ id: 'dev:' + nick, nickname: nick, role: role }));
        applyRole();
        loginMsg.textContent = nick + '님 (' + role + ') 로그인 완료.';
        setTimeout(closeLogin, 900);
      })
      .catch(function () { loginMsg.textContent = '권한 조회 실패 (네트워크 오류).'; });
  });
  applyRole();

  /* ---- Firebase /rework/* CRUD 헬퍼 (클립·일정·공지 공용) ----
     격리 경로: 운영 데이터를 건드리지 않도록 반드시 /rework/ 아래에만 쓴다.
     ⚠️ Phase A는 보안 규칙/토큰이 없어 클라이언트 신뢰에 의존한다.
        서버측 강제(soop id 소유권·admin)는 Phase B에서 커스텀 토큰 + RTDB 규칙으로 추가. */
  var REWORK_BASE = FIREBASE_BASE + '/rework';
  function jfetch(url, opt) {
    return fetch(url, opt).then(function (r) {
      if (!r.ok) throw new Error('Firebase ' + r.status);
      return (r.status === 204) ? null : r.json();
    });
  }

  /* Phase B: 쓰기 요청에 Firebase idToken(?auth=)을 첨부한다.
     idToken은 auth/callback.html이 커스텀토큰 교환 후 sessionStorage.soop_fb에 저장.
     만료 1분 전부터는 refreshToken으로 자동 갱신. 토큰이 없으면(dev 로그인 등)
     auth 없이 보내고, 서버측 RTDB 규칙이 거부하면 그때 에러가 난다. */
  function fbSession() {
    try { return JSON.parse(sessionStorage.getItem('soop_fb') || 'null'); }
    catch (e) { return null; }
  }
  function authParam() {
    var s = fbSession();
    if (!s || !s.idToken) return Promise.resolve('');
    if (Date.now() < (s.expiresAt || 0) - 60000) {
      return Promise.resolve('auth=' + encodeURIComponent(s.idToken));
    }
    if (!s.refreshToken) return Promise.resolve('auth=' + encodeURIComponent(s.idToken));
    return fetch('https://securetoken.googleapis.com/v1/token?key=' + FIREBASE_WEB_API_KEY, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'grant_type=refresh_token&refresh_token=' + encodeURIComponent(s.refreshToken)
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.id_token) return 'auth=' + encodeURIComponent(s.idToken); // 갱신 실패 → 기존 토큰으로 시도
      var ns = { idToken: d.id_token,
                 refreshToken: d.refresh_token || s.refreshToken,
                 expiresAt: Date.now() + (parseInt(d.expires_in, 10) || 3600) * 1000 };
      sessionStorage.setItem('soop_fb', JSON.stringify(ns));
      return 'auth=' + encodeURIComponent(ns.idToken);
    }).catch(function () { return 'auth=' + encodeURIComponent(s.idToken); });
  }
  function writeUrl(path) {
    return authParam().then(function (a) {
      /* 로그인 상태인데 idToken이 없으면 쓰기 불가 — 서버가 어차피 401을 돌려주므로,
         보내기 전에 사람이 읽을 수 있는 메시지로 끊는다. dev 로그인(id가 'dev:' 접두)과
         실SOOP 로그인의 토큰 교환 실패(soop_fb 미생성)를 구분해 안내한다. */
      if (!a && currentUser()) {
        var u = currentUser();
        var isDev = u && typeof u.id === 'string' && u.id.indexOf('dev:') === 0;
        throw new Error(isDev
          ? '개발용 로그인은 화면 미리보기 전용이라 저장 권한이 없습니다. 실서비스(goraesangsa.com)에서 SOOP 계정으로 로그인한 뒤 이용해 주세요.'
          : '저장 권한 토큰 발급이 완료되지 않았습니다. 로그아웃 후 SOOP 계정으로 다시 로그인해 주세요.');
      }
      return REWORK_BASE + path + (a ? '?' + a : '');
    });
  }

  var WhaleData = {
    // col: 'clips' | 'schedules' | 'notices'.  각 항목 id = Firebase push 키.
    list: function (col) {
      return jfetch(REWORK_BASE + '/' + col + '.json?v=' + Date.now()).then(function (obj) {
        if (!obj) return [];
        return Object.keys(obj).map(function (k) { var it = obj[k] || {}; it.id = k; return it; });
      });
    },
    create: function (col, data) {
      var u = currentUser();
      if (!u) return Promise.reject(new Error('로그인이 필요합니다.'));
      data.ownerId = u.id; data.ownerNick = u.nickname;
      data.createdAt = Date.now(); data.updatedAt = data.createdAt;
      return writeUrl('/' + col + '.json').then(function (url) {
        return jfetch(url,
          { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      });
    },
    update: function (col, id, patch) {
      patch.updatedAt = Date.now();
      return writeUrl('/' + col + '/' + id + '.json').then(function (url) {
        return jfetch(url,
          { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) });
      });
    },
    remove: function (col, id) {
      return writeUrl('/' + col + '/' + id + '.json').then(function (url) {
        return jfetch(url, { method: 'DELETE' });
      });
    }
  };

  /* ---- 스크롤 리빌 — IntersectionObserver, once-only (07-11: 스크롤 전수 측정 layout thrash 제거) ---- */
  function imgEvent() {   /* IO 미지원 브라우저 폴백 */
    var wt = window.scrollY + window.innerHeight;
    $$('.img-ani').forEach(function (el) {
      var it = el.getBoundingClientRect().top + window.scrollY;
      if (wt > it + 120) el.classList.add('img-aniload');
    });
  }
  if (PRM) {
    $$('.img-ani').forEach(function (el) { el.classList.add('img-aniload'); });
  } else if ('IntersectionObserver' in window) {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('img-aniload'); revealIO.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -100px 0px' });
    $$('.img-ani').forEach(function (el) { revealIO.observe(el); });
  } else {
    imgEvent();
    window.addEventListener('scroll', imgEvent, { passive: true });
    window.addEventListener('load', imgEvent);
  }

  /* 동적 렌더(Firebase clips·schedules·notices·archive 목록)로 나중에 추가되는 .img-ani도 리빌.
     위 observe는 초기 DOM만 잡아, 목록 카드가 opacity:0으로 숨은 채 남던 문제 보완. */
  if ('MutationObserver' in window) {
    new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        Array.prototype.forEach.call(m.addedNodes, function (n) {
          if (n.nodeType !== 1) return;
          var els = (n.classList && n.classList.contains('img-ani')) ? [n] : [];
          if (n.querySelectorAll) els = els.concat($$('.img-ani', n));
          els.forEach(function (el) {
            if (!PRM && revealIO) revealIO.observe(el);
            else el.classList.add('img-aniload');
          });
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }

  /* ---- 헤더 중앙 바로가기 — 현재 섹션 표시 ---- */
  $$('.h-nav a').forEach(function (a) {
    var key = (a.getAttribute('href') || '').replace('.html', '');
    if (key && location.pathname.indexOf(key) >= 0) a.classList.add('on');
  });

  /* ---- Scroll Top ---- */
  var scrollTopWrp = document.getElementById('scrollTopWrp');
  var scrollTopBtn = document.getElementById('scrollTopBtn');
  if (scrollTopWrp) {
    var chkTop = function () { scrollTopWrp.classList.toggle('on', window.scrollY > 1); };
    window.addEventListener('scroll', chkTop, { passive: true });
    chkTop();
  }
  if (scrollTopBtn) scrollTopBtn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: PRM ? 'auto' : 'smooth' });
  });

  /* ---- 멤버 프로필 모달 (재사용) ----
     페이지가 window.WHALE_MEMBERS 배열을 정의하고, 카드에 data-idx를 붙이면
     자동으로 클릭/Enter 시 모달이 열린다. 스탯 카운트업 + 이전/다음 순환. */
  var memberModalBg    = document.getElementById('memberModalBg');
  var memberModalClose = document.getElementById('memberModalClose');
  var memberModalAva   = document.getElementById('memberModalAva');
  var MEMBERS = window.WHALE_MEMBERS || [];
  var curIdx = 0;

  /* 인사기록카드 날짜 — 생일은 다음 생일까지 D-, 데뷔·입사는 지난 날수 D+ 와 연·월·일 경과.
     날짜만 다루므로 UTC 자정 기준으로 뺀다(로컬 시각·서머타임 때문에 하루 밀리는 것 방지).
     기준일은 브라우저의 오늘 — 페이지를 열 때마다 자동으로 다시 센다. */
  var DAY = 86400000;
  function todayUTC() { var d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()); }
  function birthInfo(s) {
    var p = /^(\d{2})-(\d{2})$/.exec(String(s || '')); if (!p) return null;
    var mo = +p[1], da = +p[2], t = todayUTC(), y = new Date(t).getUTCFullYear();
    var next = Date.UTC(y, mo - 1, da);
    if (next < t) next = Date.UTC(y + 1, mo - 1, da);
    var n = Math.round((next - t) / DAY);
    return { v: mo + '월 ' + da + '일', d: n === 0 ? 'D-DAY' : 'D-' + n, e: '' };
  }
  function pastInfo(s) {
    var p = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || '')); if (!p) return null;
    var t = todayUTC(), from = Date.UTC(+p[1], +p[2] - 1, +p[3]);
    var n = Math.round((t - from) / DAY), now = new Date(t);
    // 연·월·일 경과는 달력 기준 — 달마다 길이가 달라 날수 나눗셈으로는 맞출 수 없다
    var y = now.getUTCFullYear() - +p[1], mo = now.getUTCMonth() + 1 - +p[2], d = now.getUTCDate() - +p[3];
    if (d < 0) { mo--; d += new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 0)).getUTCDate(); }
    if (mo < 0) { y--; mo += 12; }
    return { v: p[1] + '-' + p[2] + '-' + p[3], d: (n >= 0 ? 'D+' : 'D') + n,
             e: y > 0 || mo > 0 || d > 0 ? y + '년 ' + mo + '개월 ' + d + '일' : '' };
  }
  function setStat(k, info) {
    var el = document.querySelector('.modal-stats .stat[data-k="' + k + '"]'); if (!el) return;
    el.querySelector('.stat-v').textContent = info ? info.v : '—';
    el.querySelector('.stat-d').textContent = info ? info.d : '';
    el.querySelector('.stat-e').textContent = info ? info.e : '';
  }
  /* 멤버 상세(member.html)도 같은 계산을 쓴다 — 홈 모달과 상세가 서로 다른 날짜를 말하면 안 된다 */
  window.WhaleDate = { birth: birthInfo, past: pastInfo };
  function escH(x) {
    var d = document.createElement('div');
    d.textContent = x == null ? '' : x;
    return d.innerHTML.replace(/"/g, '&quot;');
  }
  function fillModal(idx) {
    var m = MEMBERS[idx]; if (!m) return;
    memberModalAva.style.background = m.color || '';
    memberModalAva.innerHTML = (m.img ? '<img src="' + escH(m.img) + '" alt="' + escH(m.name) + '" onerror="this.style.display=\'none\'">' : '') + escH(m.initials || '');
    var set = function (id, v) { var e = document.getElementById(id); if (e) e.textContent = v; };
    set('memberModalDept', m.dept || '');
    var deptEl = document.getElementById('memberModalDept');
    /* 부서 그라데이션 위 어두운 스크림 — 밝은 색 끝단에서도 흰 글자 대비 확보 */
    if (deptEl) deptEl.style.background = m.color
      ? 'linear-gradient(rgba(5,7,18,.38),rgba(5,7,18,.38)),' + m.color : '';
    set('memberModalName', m.name || '');
    set('memberModalRole', m.role || '');
    set('memberModalBio',  m.bio || '');
    setStat('birth',  birthInfo(m.birth));
    setStat('debut',  pastInfo(m.debut));
    setStat('joined', pastInfo(m.joined));
  }
  function openMember(idx) { if (!memberModalBg) return; curIdx = idx; fillModal(idx); memberModalBg.hidden = false; }
  function closeMember()   { if (memberModalBg) memberModalBg.hidden = true; }

  if (memberModalBg && MEMBERS.length) {
    $$('[data-idx]').forEach(function (card) {
      var idx = parseInt(card.getAttribute('data-idx'), 10);
      if (isNaN(idx)) return;
      card.addEventListener('click', function () { openMember(idx); });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openMember(idx); }
      });
    });
    if (memberModalClose) memberModalClose.addEventListener('click', closeMember);
    memberModalBg.addEventListener('click', function (e) { if (e.target === memberModalBg) closeMember(); });
    var mp = document.getElementById('memberModalPrev'), mn = document.getElementById('memberModalNext');
    if (mp) mp.addEventListener('click', function () { curIdx = (curIdx - 1 + MEMBERS.length) % MEMBERS.length; fillModal(curIdx); });
    if (mn) mn.addEventListener('click', function () { curIdx = (curIdx + 1) % MEMBERS.length; fillModal(curIdx); });
  }

  /* ---- 이미지 저장 방지 (운영본 image-protect.js 이식) ----
     우클릭 저장·드래그 저장만 차단 — 완전 차단은 불가(개발자도구로 우회 가능) */
  document.addEventListener('contextmenu', function (e) {
    if (e.target.tagName === 'IMG') e.preventDefault();
  });
  document.addEventListener('dragstart', function (e) {
    if (e.target.tagName === 'IMG') e.preventDefault();
  });

  /* ---- 모달 포커스 관리 — 열릴 때 이동, Tab 순환, 닫힐 때 복귀 (role=dialog 공통) ---- */
  var lastModalFocus = null;
  function modalFocusables(root) {
    return $$('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])', root)
      .filter(function (el) { return !el.disabled && el.offsetParent !== null; });
  }
  $$('[role="dialog"][aria-modal="true"]').forEach(function (d) {
    new MutationObserver(function () {
      if (!d.hidden) {
        lastModalFocus = document.activeElement;
        var f = modalFocusables(d);
        if (f[0]) f[0].focus(); else { d.setAttribute('tabindex', '-1'); d.focus(); }
      } else if (lastModalFocus) {
        try { lastModalFocus.focus(); } catch (e) {}
        lastModalFocus = null;
      }
    }).observe(d, { attributes: true, attributeFilter: ['hidden'] });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    var d = null;
    $$('[role="dialog"][aria-modal="true"]').forEach(function (x) { if (!x.hidden) d = x; });
    if (!d) return;
    var f = modalFocusables(d); if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && (document.activeElement === last || !d.contains(document.activeElement))) { e.preventDefault(); first.focus(); }
  });

  /* ---- 공용 ESC ---- */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (menuOpen) closeGnb();
    if (loginModalBg && !loginModalBg.hidden) closeLogin();
    if (memberModalBg && !memberModalBg.hidden) closeMember();
  });

  /* 외부에서 쓸 수 있게 노출 */
  window.WhaleUI = { openMember: openMember, closeMember: closeMember, applyRole: applyRole,
                     getUser: currentUser, isAdmin: isAdmin, isLoggedIn: isLoggedIn, canEdit: canEdit };
  window.WhaleData = WhaleData;

  /* 사이트 자체 조회수 — /rework/clipviews/{clipId} = 숫자 하나.
     로그인 없이 쓰지만 규칙이 '1씩 증가'만 허용한다(임의값·감소·삭제 거부).
     경합이 나면 서버가 그 쓰기를 거부할 뿐 덮어쓰기 유실은 없다 → 조용히 무시. */
  window.WhaleViews = {
    // 전체 카운터를 한 번에 읽어 목록에 합류. 실패해도 화면은 그대로(0으로 표시).
    load: function (items) {
      return jfetch(REWORK_BASE + '/clipviews.json?v=' + Date.now())
        .then(function (v) { return v || {}; })
        .catch(function () { return {}; })
        .then(function (v) {
          (items || []).forEach(function (c) { c.views = v[c.id] || 0; });
          return items;
        });
    },
    // 상세 진입 시 1회. 같은 세션의 새로고침은 sessionStorage로 막는다.
    bump: function (id) {
      if (!id) return;
      var k = 'cv:' + id;
      try { if (sessionStorage.getItem(k)) return; sessionStorage.setItem(k, '1'); } catch (e) {}
      var u = REWORK_BASE + '/clipviews/' + encodeURIComponent(id) + '.json';
      fetch(u).then(function (r) { return r.json(); }).then(function (n) {
        return fetch(u, { method: 'PUT', body: String((Number(n) || 0) + 1) });
      }).catch(function () {});
    }
  };
})();

/* 공유 임베드 헬퍼(window.WhaleEmbed)는 assets/embed.js로 분리 — 홈(index.html)도 같은 한 벌을 쓴다. */
