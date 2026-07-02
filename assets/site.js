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
  }
  if (hambBtn && gnbOverlay) {
    hambBtn.addEventListener('click', function () { menuOpen ? closeGnb() : openGnb(); });
    $$('a', gnbOverlay).forEach(function (a) { a.addEventListener('click', closeGnb); });
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

  function currentUser() {
    try { return JSON.parse(sessionStorage.getItem('soop_user') || 'null'); }
    catch (e) { return null; }
  }
  function hasAdmin(u) { u = u || currentUser(); return !!(u && (u.role === 'admin' || u.role === 'editor')); }

  function applyRole() {
    var u = currentUser(), admin = hasAdmin(u);
    $$('.admin-only').forEach(function (el) { el.classList.toggle('is-shown', admin); });
    if (!loginBtn) return;
    if (admin) {
      loginBtn.textContent = (u.nickname || '관리자') + ' ⏏';
      loginBtn.classList.add('is-admin');
      loginBtn.title = '로그아웃 (' + u.role + ')';
    } else {
      loginBtn.textContent = '로그인';
      loginBtn.classList.remove('is-admin');
      loginBtn.title = '';
    }
  }

  function soopLogin() {
    sessionStorage.setItem('soop_return', location.pathname + location.search);
    var p = new URLSearchParams({ response_type: 'code', client_id: SOOP_CLIENT_ID, redirect_uri: REDIRECT_URI });
    location.href = SOOP_AUTH_URL + '?' + p.toString();
  }
  function openLogin()  { if (loginModalBg) loginModalBg.hidden = false; }
  function closeLogin() { if (loginModalBg) loginModalBg.hidden = true; if (loginMsg) loginMsg.textContent = ''; }

  if (loginBtn) loginBtn.addEventListener('click', function () {
    if (hasAdmin()) { sessionStorage.removeItem('soop_user'); applyRole(); return; }
    openLogin();
  });
  if (loginClose) loginClose.addEventListener('click', closeLogin);
  if (loginModalBg) loginModalBg.addEventListener('click', function (e) { if (e.target === loginModalBg) closeLogin(); });
  if (soopLoginBtn) soopLoginBtn.addEventListener('click', soopLogin);

  if (devLoginForm) devLoginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var nick = devLoginForm.querySelector('[name="nick"]').value.trim();
    if (!nick) { loginMsg.textContent = '숲 닉네임을 입력하세요.'; return; }
    loginMsg.textContent = '권한 확인 중...';
    fetch(FIREBASE_BASE + '/permissions/' + encodeURIComponent(nick) + '.json')
      .then(function (r) { return r.json(); })
      .then(function (perm) {
        var role = (perm === 'admin' || perm === 'editor') ? perm : 'none';
        if (role === 'none') { loginMsg.textContent = '"' + nick + '" 계정에는 관리자 권한이 없습니다.'; return; }
        sessionStorage.setItem('soop_user', JSON.stringify({ nickname: nick, role: role }));
        applyRole();
        loginMsg.textContent = nick + '님 (' + role + ') 로그인 완료.';
        setTimeout(closeLogin, 900);
      })
      .catch(function () { loginMsg.textContent = '권한 조회 실패 (네트워크 오류).'; });
  });
  applyRole();

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

  /* ---- 공용 ESC ---- */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (menuOpen) closeGnb();
    if (loginModalBg && !loginModalBg.hidden) closeLogin();
    if (memberModalBg && !memberModalBg.hidden) closeMember();
  });

  /* 외부에서 쓸 수 있게 노출 */
  window.WhaleUI = { openMember: openMember, closeMember: closeMember, applyRole: applyRole };
})();
