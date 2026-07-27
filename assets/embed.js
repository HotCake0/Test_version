/* ── 공유 임베드 헬퍼 (§2.6-2, 아카이브 상세 인라인에서 승격) ──────────────
   YouTube/SOOP VOD url → 임베드 플레이어 url, 그 외/검증 실패 → null.
   ⚠️보안: 부분일치(indexOf)는 evil.com/sooplive.com 류 우회가 되므로 new URL로
   호스트를 엄격 검증(정확일치 또는 .접미사)하고, 원본을 그대로 넘기지 않고
   검증된 조각으로만 재조립한다. C-2 임베드 보안 매트릭스의 검증 대상. */
window.WhaleEmbed = (function () {
  function hostMatch(h, d) { return h === d || h.slice(-(d.length + 1)) === '.' + d; }
  return function (u) {
    var pu;
    try { pu = new URL((u == null ? '' : String(u)).trim()); } catch (e) { return null; }
    if (pu.protocol !== 'https:' && pu.protocol !== 'http:') return null;
    var host = pu.hostname.toLowerCase();
    // YouTube — 검증된 videoId(문자/숫자/-/_)로만 재조립
    if (hostMatch(host, 'youtu.be')) {
      var sid = pu.pathname.replace(/^\/+/, '').split('/')[0];
      return /^[\w-]{6,}$/.test(sid) ? 'https://www.youtube.com/embed/' + sid : null;
    }
    if (hostMatch(host, 'youtube.com') || hostMatch(host, 'youtube-nocookie.com')) {
      var vid = pu.searchParams.get('v');
      if (!vid) { var me = pu.pathname.match(/^\/embed\/([\w-]{6,})/); if (me) vid = me[1]; }
      return (vid && /^[\w-]{6,}$/.test(vid)) ? 'https://www.youtube.com/embed/' + vid : null;
    }
    // SOOP VOD — 숫자 player id로만 재조립(원본 패스스루 금지)
    if (hostMatch(host, 'sooplive.com') || hostMatch(host, 'sooplive.co.kr')) {
      var pm = pu.pathname.match(/\/player\/(\d+)/);
      if (pm) return 'https://' + host + '/player/' + pm[1] + '/embed';
      if (/\/embed(\/|$)/.test(pu.pathname)) return 'https://' + host + pu.pathname;
    }
    return null;
  };
})();
