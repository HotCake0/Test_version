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
  }
  function closeGnb() {
    menuOpen = false;
    gnbOverlay.classList.remove('active');
    gnbOverlay.setAttribute('aria-hidden', 'true');
    hambBtn.setAttribute('aria-expanded', 'false');
    hambBtn.setAttribute('aria-label', '메뉴 열기');
    document.body.style.overflow = '';
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
    return authParam().then(function (a) { return REWORK_BASE + path + (a ? '?' + a : ''); });
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

  /* ---- 스크롤 리빌 (홈과 동일 img-ani 공식) ---- */
  function imgEvent() {
    var wt = window.scrollY + window.innerHeight;
    $$('.img-ani').forEach(function (el) {
      var it = el.getBoundingClientRect().top + window.scrollY;
      if (wt > it + 120) el.classList.add('img-aniload');
      else if (window.innerWidth > 768) el.classList.remove('img-aniload');
    });
  }
  if (PRM) {
    $$('.img-ani').forEach(function (el) { el.classList.add('img-aniload'); });
  } else {
    imgEvent();
    window.addEventListener('scroll', imgEvent, { passive: true });
    window.addEventListener('load', imgEvent);
  }

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

  function countUp(el, target) {
    if (PRM) { el.textContent = target.toLocaleString(); return; }
    var st = null, dur = 1200;
    (function step(ts) {
      if (!st) st = ts;
      var p = Math.min((ts - st) / dur, 1);
      el.textContent = Math.floor((1 - Math.pow(1 - p, 3)) * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
    })(performance.now());
  }
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
    (m.stats || []).forEach(function (s, i) {
      var en = document.getElementById('mstat' + i), eu = document.getElementById('mstat' + i + 'u');
      if (en) countUp(en, s.n); if (eu) eu.textContent = s.u;
    });
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
})();
