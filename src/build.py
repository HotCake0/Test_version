#!/usr/bin/env python3
# =========================================================
# 고래상사 하위 페이지 빌더 (v2 — 실(實)페이지)
# src/content/*.json  ->  pages/*.html
# 공유 자산: assets/site.css · assets/site.js (메인 홈과 동일 디자인 시스템)
# 페이지는 pages/ 안에 위치 → 자원 경로는 ../assets, ../img, ../index.html
# =========================================================
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
OUT = os.path.join(HERE, "..", "pages")
os.makedirs(OUT, exist_ok=True)


def esc(s):
    return html.escape(str(s if s is not None else ""))


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


SITE = load("site.json")
MEMBERS = load("members.json")["members"]
CLIPS = load("clips.json")["clips"]
ARCHIVE = load("archive.json")["archive"]
SCHEDULE = load("schedule.json")["schedule"]
NOTICES = load("notices.json")["notices"]

# slug -> (group, page) 조회용
PAGE_BY_SLUG = {}
for g in SITE["groups"]:
    for p in g["pages"]:
        PAGE_BY_SLUG[p["slug"]] = (g, p)


def href(slug):
    """pages/ 내부 기준 상대경로. home은 ../index.html."""
    gp = PAGE_BY_SLUG.get(slug)
    if gp and gp[1].get("home"):
        return "../index.html"
    return f"{slug}.html"


# ---------- 공유 partial ----------

# og:image 등 소셜 스크레이퍼용 절대경로. canonical 경로는 라우팅 확정(ROADMAP §3-B) 후 별도 추가.
BASE_URL = "https://goraesangsa.com"


def page_description(slug):
    """페이지별 meta description (site.json label 기반 합성)."""
    gp = PAGE_BY_SLUG.get(slug)
    if gp:
        return f"고래상사 {gp[1]['label']} — 크루 16인의 방송·클립·일정·아카이브를 한 곳에서."
    return "고래상사 크루 공식 사이트 — 방송·클립·일정·아카이브를 한 곳에서."


def head(title, page_css="", slug=None):
    css = f"<style>{page_css}</style>" if page_css else ""
    ttl = f"{title} · 고래상사"
    desc = page_description(slug)
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-store">
<title>{esc(ttl)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="고래상사">
<meta property="og:title" content="{esc(ttl)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE_URL}/favicon.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<script>if(!matchMedia('(prefers-reduced-motion:reduce)').matches)document.documentElement.classList.add('js-anim');</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" rel="stylesheet">
<link rel="stylesheet" href="../assets/site.css">
{css}</head><body>
<div class="wavebg" aria-hidden="true"></div>
<div class="veil" aria-hidden="true"></div>"""


def header_and_drawer(current_slug):
    groups_html = []
    for g in SITE["groups"]:
        sub = []
        for p in g["pages"]:
            if p.get("detail"):
                continue  # 상세 페이지는 드로어 목차에서 숨김(진입점 아님)
            cls = ' class="active"' if p["slug"] == current_slug else ""
            sub.append(
                f'<li><a{cls} href="{href(p["slug"])}">'
                f'<span class="sn">{g["no"].lstrip("0")}-{len([x for x in g["pages"][:g["pages"].index(p)+1] if not x.get("detail")])}</span>'
                f'{esc(p["label"])}</a></li>')
        grp_cls = "grp admin-only" if g.get("admin") else "grp"
        groups_html.append(
            f'<li class="{grp_cls}">'
            f'<button class="grp-t" type="button" aria-expanded="false"><span class="mn">{g["no"]}</span>{esc(g["title"])}</button>'
            f'<ul class="gnb-sub">{"".join(sub)}</ul></li>')

    header = """<header id="header"><div class="header-in">
    <a class="h-logo" href="../index.html">고래<span class="lk">상사</span></a>
    <div class="h-right">
      <button class="btn-login" id="loginBtn" type="button">로그인</button>
      <button class="hamb" id="hambBtn" type="button" aria-label="메뉴 열기"
        aria-expanded="false" aria-controls="gnbOverlay"><span></span><span></span><span></span></button>
    </div></div></header>"""

    drawer = ('<div class="gnb-overlay" id="gnbOverlay" aria-hidden="true">'
              '<nav aria-label="주요 메뉴"><ul class="gnb-menu">'
              + "".join(groups_html) +
              '</ul></nav>'
              '<div class="gnb-btm">'
              '<a href="../index.html">메인 홈</a>'
              '<a href="multiview.html">멀티뷰</a>'
              '</div></div>')
    return header + drawer


def footer():
    return """<footer class="site-footer">
  <div class="footer-in">
    <span class="footer-logo">고래<span class="lk">상사</span></span>
    <div class="footer-links">
      <a class="btn sm ghost" href="notices.html">공지사항</a>
      <a class="btn sm ghost admin-only" href="admin.html">관리자 페이지</a>
      <a class="btn sm ghost" href="../index.html">메인으로</a>
    </div>
  </div>
  <div class="footer-copy">© <span id="footerYear"></span> 고래상사 (Whale-Corp). 회사 역할극 버추얼 크루 · 16인.</div>
</footer>
<div class="scroll-topwrp" id="scrollTopWrp">
  <button class="scroll-top-btn" id="scrollTopBtn" type="button" aria-label="맨 위로 이동">
    <span class="ar" aria-hidden="true">↑</span>TOP</button>
</div>"""


def login_modal():
    return """<div class="login-modal-bg" id="loginModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="loginTitle">
  <div class="login-modal">
    <button class="login-close" id="loginClose" type="button" aria-label="닫기">×</button>
    <h2 id="loginTitle">로그인</h2>
    <p class="sub">숲(SOOP) 계정으로 로그인합니다. 관리자 권한은 숲 아이디로 확인됩니다.</p>
    <button class="btn primary login-soop" id="soopLoginBtn" type="button">🔵 숲(SOOP) 계정으로 로그인</button>
    <p class="login-msg" id="loginMsg" role="status" aria-live="polite"></p>
    <details class="dev-login">
      <summary>개발용 로그인 (로컬 테스트)</summary>
      <form id="devLoginForm" novalidate>
        <label class="field"><span>숲 닉네임</span>
          <input type="text" name="nick" placeholder="숲 닉네임으로 권한 조회" autocomplete="off"></label>
        <button class="btn" type="submit">권한 확인 후 로그인</button>
      </form>
      <p class="dev-note">실제 숲 OAuth 없이, 입력한 닉네임의 Firebase 권한만 조회해 로그인합니다. (localhost 테스트용)</p>
    </details>
  </div>
</div>"""


def member_modal():
    return """<div class="member-modal-bg" id="memberModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="memberModalName">
  <div class="member-modal">
    <button class="modal-close" id="memberModalClose" type="button" aria-label="닫기">×</button>
    <div class="modal-ava" id="memberModalAva"></div>
    <div class="modal-body">
      <div class="modal-dept" id="memberModalDept"></div>
      <div class="modal-name" id="memberModalName"></div>
      <div class="modal-role" id="memberModalRole"></div>
      <div class="modal-bio"  id="memberModalBio"></div>
      <div class="modal-stats">
        <div class="stat"><div class="stat-n" id="mstat0">0</div><div class="stat-u" id="mstat0u">—</div></div>
        <div class="stat"><div class="stat-n" id="mstat1">0</div><div class="stat-u" id="mstat1u">—</div></div>
        <div class="stat"><div class="stat-n" id="mstat2">0</div><div class="stat-u" id="mstat2u">—</div></div>
      </div>
      <div class="modal-nav-row">
        <button class="btn sm" id="memberModalPrev" type="button">← 이전</button>
        <button class="btn sm" id="memberModalNext" type="button">다음 →</button>
      </div>
    </div>
  </div>
</div>"""


def page_head_block(en, eyebrow, sub):
    """그룹 EN 윤곽선 헤더 (디자인 시스템 섹션 헤더 패턴)."""
    return ('<header class="pg-head img-ani bottom-top">'
            f'<span class="pg-eyebrow">{esc(eyebrow)}</span>'
            f'<h1 class="pg-en">{esc(en)}</h1>'
            f'<p class="pg-sub">{esc(sub)}</p></header>')


def tail(scripts=""):
    return f"""{login_modal()}
<script src="../assets/site.js"></script>
{scripts}
</body></html>"""


def write(slug, title, body, page_css="", scripts="", need_member_modal=False):
    mm = member_modal() if need_member_modal else ""
    doc = (head(title, page_css, slug)
           + header_and_drawer(slug)
           + '<main class="pg-wrap">' + body + '</main>'
           + footer() + mm + tail(scripts))
    with open(os.path.join(OUT, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(doc)


# ---------- 공통 페이지 CSS (site.css 위에 얹는 하위페이지 레이아웃) ----------
PAGE_CSS = """
.pg-wrap{max-width:var(--maxw);margin:0 auto;padding:calc(72px + clamp(40px,7vw,110px)) var(--pad) clamp(80px,10vw,140px);min-height:70vh}
.pg-head{margin-bottom:clamp(32px,5vw,64px)}
.pg-eyebrow{display:block;font-size:12px;font-weight:800;letter-spacing:.2em;color:var(--brand);text-transform:uppercase;margin-bottom:12px}
.pg-en{margin:0 0 10px;font-size:clamp(40px,6vw,84px);font-weight:900;letter-spacing:-.04em;line-height:1;
  color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.18)}
.pg-sub{margin:0;font-size:clamp(15px,1.4vw,18px);color:var(--ink-2)}
/* 필터 바 */
.pg-tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:clamp(24px,3vw,40px)}
.chip{font:inherit;font-size:13px;font-weight:700;padding:8px 16px;border-radius:999px;
  border:1px solid var(--line-2);background:var(--surface-2);color:var(--ink-2);cursor:pointer;transition:.15s}
.chip:hover{border-color:var(--brand);color:var(--ink)}
.chip.active{background:var(--brand);border-color:var(--brand);color:#fff}
.pg-count{margin-left:auto;font-size:13px;color:var(--ink-2)}
/* 멤버 그리드 */
.mgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(16px,2vw,26px)}
@media(max-width:1000px){.mgrid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:760px){.mgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:440px){.mgrid{grid-template-columns:1fr}}
.mcard{position:relative;aspect-ratio:3/4;border-radius:14px;overflow:hidden;cursor:pointer;
  background:var(--surface);border:1px solid var(--line);
  transition:border-color .3s var(--ease),box-shadow .3s var(--ease),transform .3s var(--ease)}
.mcard:hover{border-color:var(--brand);box-shadow:0 14px 44px rgba(47,99,255,.3);transform:translateY(-4px)}
.mcard .ava-ph{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:clamp(38px,6vw,64px);font-weight:900;color:rgba(255,255,255,.88)}
.mcard .ava-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(1.25) contrast(1.04);transition:transform .5s var(--ease)}
.mcard:hover .ava-img{transform:scale(1.06)}
.mcard .card-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.8) 0%,transparent 58%);z-index:1}
.mcard .card-info{position:absolute;left:0;right:0;bottom:0;padding:14px;z-index:2}
.mcard .card-name{font-size:17px;font-weight:900;letter-spacing:-.02em}
.mcard .card-role{font-size:12px;color:rgba(255,255,255,.7);margin-top:2px}
.mcard .card-tag{display:inline-block;margin-top:6px;font-size:11px;font-weight:700;background:rgba(255,255,255,.14);padding:3px 9px;border-radius:999px;color:rgba(255,255,255,.82)}
.mcard.is-live{border-color:var(--hot)}
.mcard.is-live:hover{box-shadow:0 14px 44px rgba(255,77,77,.32)}
.mlive{position:absolute;top:10px;left:10px;z-index:3;display:inline-flex;align-items:center;gap:5px;
  font-size:11px;font-weight:800;letter-spacing:.04em;padding:4px 9px;border-radius:7px;background:var(--hot);color:#fff;
  box-shadow:0 4px 14px rgba(255,77,77,.5)}
.mlive[hidden]{display:none}  /* [hidden] 속성이 위 display:inline-flex에 밀리므로 명시 필요(오프라인 오표시 방지) */
.mlive .d{width:6px;height:6px;border-radius:50%;background:#fff;animation:pulse 1.8s infinite}
.mlive .mv-n{font-weight:700;opacity:.9}
.mlive:hover{background:#ff1f4b}
@media(prefers-reduced-motion:reduce){.mlive .d{animation:none}}
/* 크루 소개 히어로 */
.crew-hero{display:grid;grid-template-columns:1.2fr 1fr;gap:clamp(24px,4vw,64px);align-items:center;margin-bottom:clamp(48px,7vw,100px)}
@media(max-width:860px){.crew-hero{grid-template-columns:1fr}}
.crew-hero h2{font-size:clamp(28px,4vw,52px);font-weight:900;letter-spacing:-.03em;line-height:1.15;margin:0 0 18px;word-break:keep-all}
.crew-hero h2 em{font-style:normal;color:var(--accent)}
.crew-hero p{font-size:clamp(15px,1.4vw,18px);color:var(--ink-2);line-height:1.7;margin:0 0 14px;word-break:keep-all}
.crew-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:26px}
.crew-metric{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px 14px;text-align:center}
.crew-metric .n{font-size:clamp(24px,3vw,38px);font-weight:900;letter-spacing:-.02em;color:var(--ink)}
.crew-metric .u{font-size:12px;color:var(--ink-2);margin-top:4px}
.crew-visual{aspect-ratio:4/5;border-radius:18px;background:linear-gradient(135deg,#0b2e8f,#2f6bff,#0a44cc);position:relative;overflow:hidden;box-shadow:var(--shadow)}
.crew-visual::after{content:"🐋";position:absolute;right:6%;bottom:2%;font-size:clamp(120px,20vw,240px);opacity:.14;line-height:1}
/* 부서 리스트 */
.dept-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-top:clamp(28px,4vw,48px)}
.dept-card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 20px;transition:border-color .25s,transform .25s}
.dept-card:hover{border-color:var(--line-2);transform:translateY(-3px)}
.dept-card h3{margin:0 0 6px;font-size:19px;font-weight:900;letter-spacing:-.02em}
.dept-card .dept-count{font-size:12px;color:var(--accent);font-weight:800;letter-spacing:.08em}
.dept-card .dept-mem{margin-top:12px;font-size:13.5px;color:var(--ink-2);line-height:1.7}
/* 준비중 스텁 */
.stub{text-align:center;padding:clamp(48px,10vw,120px) 0;color:var(--ink-2)}
.stub .big{font-size:clamp(40px,7vw,88px);margin-bottom:18px;opacity:.5}
.stub h2{font-size:clamp(22px,3vw,32px);font-weight:900;color:var(--ink);margin:0 0 12px;letter-spacing:-.02em}
.stub p{font-size:15px;line-height:1.7;margin:0 auto;max-width:440px}
.stub .btn{margin-top:26px}
/* 멤버 상세 */
.mdetail{display:grid;grid-template-columns:.9fr 1.3fr;gap:clamp(24px,4vw,56px);align-items:start}
@media(max-width:820px){.mdetail{grid-template-columns:1fr}}
.mdetail .portrait{aspect-ratio:3/4;border-radius:18px;overflow:hidden;position:relative;box-shadow:var(--shadow);border:1px solid var(--line-2)}
.mdetail .portrait .ava-ph{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:clamp(56px,9vw,120px);font-weight:900;color:rgba(255,255,255,.9)}
.mdetail .portrait img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.mdetail .dept-label{font-size:12px;font-weight:800;letter-spacing:.18em;color:var(--accent);text-transform:uppercase}
.mdetail h2{margin:8px 0 6px;font-size:clamp(30px,4.4vw,56px);font-weight:900;letter-spacing:-.03em}
.mdetail .role{font-size:15px;color:var(--ink-2);margin-bottom:20px}
.mdetail .bio{font-size:clamp(15px,1.4vw,17px);color:#c3cee6;line-height:1.75;margin-bottom:26px;word-break:keep-all}
.mdetail .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:26px}
.mdetail .stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 10px;text-align:center}
.mdetail .stat .n{font-size:clamp(20px,2.4vw,30px);font-weight:900;letter-spacing:-.02em}
.mdetail .stat .u{font-size:11px;color:var(--ink-2);margin-top:4px}
.mdetail .navrow{display:flex;gap:10px;flex-wrap:wrap}
.mdetail .soop-row{margin:0 0 14px}
.mdetail .soop-row .btn{width:100%;justify-content:center;font-weight:800}
/* 상세 라이브 임베드 (방송중일 때 초상 대신 노출) */
.mdetail .media-live{position:relative;border-radius:18px;overflow:hidden;box-shadow:var(--shadow);border:1px solid var(--line-2);background:#0a0f1e}
.mdetail .media-live .embed{position:relative;aspect-ratio:16/9;width:100%}
.mdetail .media-live iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.mdetail .live-tag{position:absolute;top:12px;left:12px;z-index:2;display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:800;letter-spacing:.04em;padding:5px 11px;border-radius:8px;background:var(--hot);color:#fff;box-shadow:0 4px 14px rgba(255,77,77,.5)}
.mdetail .live-tag .d{width:6px;height:6px;border-radius:50%;background:#fff;animation:pulse 1.8s infinite}
@media(prefers-reduced-motion:reduce){.mdetail .live-tag .d{animation:none}}
.mdetail .live-title{padding:12px 14px;font-size:14px;font-weight:700;color:var(--ink);background:var(--surface);border-top:1px solid var(--line);word-break:keep-all}
/* 클립 갤러리 대표 섹션 */
.clips-hero{display:grid;grid-template-columns:1.4fr 1fr;gap:clamp(24px,3.6vw,56px);align-items:center;margin-bottom:clamp(40px,6vw,80px)}
@media(max-width:900px){.clips-hero{grid-template-columns:1fr}}
.clips-hero-info{padding-top:8px}
.ch-cat{font-size:11px;font-weight:800;letter-spacing:.15em;color:var(--accent);text-transform:uppercase;margin-bottom:10px}
.ch-title{font-size:clamp(18px,2.4vw,30px);font-weight:900;letter-spacing:-.03em;line-height:1.25;margin:0 0 12px;word-break:keep-all}
.ch-meta{font-size:13px;color:var(--ink-2);margin-bottom:14px;display:flex;gap:12px;flex-wrap:wrap}
.ch-dur{color:var(--accent);font-weight:700}
.ch-desc{font-size:14.5px;color:var(--ink-2);line-height:1.7;margin:0 0 20px;word-break:keep-all}
/* 클립 카드 그리드 */
.cgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.8vw,22px);margin-top:clamp(24px,3vw,36px)}
@media(max-width:1100px){.cgrid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:700px){.cgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:420px){.cgrid{grid-template-columns:1fr}}
.ccard{position:relative;border-radius:14px;overflow:hidden;cursor:pointer;
  background:var(--surface);border:1px solid var(--line);
  transition:border-color .3s var(--ease),box-shadow .3s var(--ease),transform .3s var(--ease)}
.ccard:hover{border-color:var(--brand);box-shadow:0 14px 44px rgba(47,99,255,.3);transform:translateY(-4px)}
.ccard-thumb{position:relative;aspect-ratio:16/9;overflow:hidden;background:#0f1730}
.ccard-thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .5s var(--ease)}
.ccard:hover .ccard-thumb img{transform:scale(1.06)}
.ccard-grad{position:absolute;inset:0}
.cplay{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:42px;height:30px;border-radius:8px;background:#ff0033;color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:13px;z-index:2;
  box-shadow:0 6px 20px rgba(0,0,0,.55);transition:transform .2s var(--ease),background .2s var(--ease)}
.ccard:hover .cplay{transform:translate(-50%,-50%) scale(1.1);background:#ff1f4b}
.ccard-info{padding:11px 13px 13px}
.ccard-title{font-size:13px;font-weight:800;letter-spacing:-.02em;line-height:1.35;
  word-break:keep-all;margin-bottom:6px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.ccard-meta{font-size:11.5px;color:var(--ink-2);display:flex;gap:7px;flex-wrap:wrap}
.ccard-dur{color:var(--accent);font-weight:700}
/* 클립 상세 */
.cdetail-player{aspect-ratio:16/9;border-radius:16px;overflow:hidden;background:#0f1730;
  position:relative;border:1px solid var(--line);box-shadow:var(--shadow);margin-bottom:22px}
.cm-cat{font-size:11px;font-weight:800;letter-spacing:.15em;color:var(--accent);
  text-transform:uppercase;margin-bottom:10px}
.cdetail-title{font-size:clamp(20px,2.8vw,36px);font-weight:900;letter-spacing:-.03em;
  line-height:1.25;margin:0 0 12px;word-break:keep-all}
.cdetail-meta{font-size:13px;color:var(--ink-2);display:flex;flex-wrap:wrap;
  gap:6px 16px;margin-bottom:14px}
.cdetail-desc{font-size:clamp(15px,1.4vw,17px);color:var(--ink-2);line-height:1.75;
  margin:0 0 22px;word-break:keep-all}
.cdetail-nav{display:flex;gap:10px;margin-bottom:36px;flex-wrap:wrap}
.crelated-head{font-size:15px;font-weight:900;letter-spacing:-.02em;
  margin:0 0 0;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:0}

/* ---- CRUD 공용: 목록 액션 / 행 관리버튼 / 작성-수정 모달 (공지 구현에서 승격, 클립·일정도 공유) ---- */
.n-actions{display:flex;flex-wrap:wrap;gap:10px;margin:-6px 0 22px}
.n-row-actions{display:flex;gap:6px;flex-wrap:wrap;flex:0 0 auto}
.n-btn{font:inherit;font-size:12px;font-weight:700;padding:6px 10px;border-radius:8px;
  border:1px solid var(--line-2);background:var(--surface-2);color:var(--ink-2);cursor:pointer;
  transition:.15s;flex:0 0 auto}
.n-btn:hover{border-color:var(--brand);color:var(--ink)}
.n-btn.pin-on{border-color:var(--warn);color:var(--warn)}
.n-btn.del:hover{border-color:var(--hot);color:var(--hot)}
.nlist-msg{padding:44px 0;text-align:center;color:var(--ink-2);font-size:14px}
/* 모바일: 수정/삭제 오탭 방지 — 터치 타겟 확대 + 버튼 간격 */
@media(max-width:640px){.n-row-actions{flex:1 1 100%;order:4;gap:10px}
  .n-btn{min-height:40px;padding:9px 14px;font-size:13px}}

.n-modal-bg{position:fixed;inset:0;z-index:170;display:flex;align-items:center;justify-content:center;
  padding:24px;background:rgba(3,6,14,.8);backdrop-filter:blur(6px)}
.n-modal-bg[hidden]{display:none}
.n-modal{width:100%;max-width:540px;max-height:88vh;overflow-y:auto;background:#0e1326;border:1px solid var(--line-2);
  border-radius:18px;padding:30px 28px 26px;box-shadow:0 30px 80px rgba(0,0,0,.7);
  position:relative;animation:modalIn .26s var(--ease)}
.n-modal h2{margin:0 0 18px;font-size:22px;font-weight:800;letter-spacing:-.02em}
.n-modal-close{position:absolute;top:14px;right:16px;border:none;background:none;
  font-size:26px;line-height:1;color:var(--ink-2);cursor:pointer;padding:4px}
.n-modal-close:hover{color:var(--ink)}
.n-modal .field select,.n-modal .field textarea{width:100%;font:inherit;font-size:15px;padding:11px 13px;
  border:1px solid var(--line-2);border-radius:10px;background:rgba(255,255,255,.04);
  color:var(--ink);transition:border-color .15s,background .15s}
.n-modal .field select:focus,.n-modal .field textarea:focus{outline:none;border-color:var(--brand);background:rgba(255,255,255,.07)}
.n-modal .field textarea{resize:vertical;min-height:130px;line-height:1.6;font-family:inherit}
.n-modal .field select option{background:#0e1524;color:var(--ink)}
.n-pin-field{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--ink-2);cursor:pointer;margin-bottom:14px}
.n-pin-field input{width:16px;height:16px;accent-color:var(--brand)}
.n-modal .btn{width:100%;justify-content:center;padding:12px;margin-top:6px}
.n-modal-msg{margin:12px 0 0;font-size:13px;text-align:center;color:#bdd0ff;min-height:18px}
/* 클립 카드/히어로 관리 배지·액션 여백 (클립 CRUD 전용) */
.ccard-actions{padding:0 13px 13px;margin-top:-4px}
.ccard-feat{position:absolute;top:8px;left:8px;z-index:3;font-size:10px;font-weight:800;letter-spacing:.03em;
  padding:3px 8px;border-radius:999px;background:var(--warn);color:#1a1400}
.clips-hero-info .n-row-actions{margin:0 0 14px}
"""


# ---------- 멤버 카드 컴포넌트 ----------

def member_card(m, idx, tag="mcard"):
    img = (f'<img class="ava-img" src="../{esc(m["img"])}" alt="{esc(m["name"])}" '
           f'onerror="this.style.display=\'none\'">') if m.get("img") else ""
    return (f'<article class="{tag}" data-idx="{idx}" data-soop="{esc(m.get("soop",""))}" '
            f'role="button" tabindex="0" aria-label="{esc(m["name"])} 프로필 보기">'
            f'<a class="mlive" hidden target="_blank" rel="noopener" aria-label="방송 보기">'
            f'<span class="d"></span>LIVE <b class="mv-n"></b></a>'
            f'{img}<div class="ava-ph" style="background:{esc(m["color"])}">{esc(m["initials"])}</div>'
            f'<div class="card-overlay"></div><div class="card-info">'
            f'<div class="card-name">{esc(m["name"])}</div>'
            f'<div class="card-role">{esc(m["role"])}</div>'
            f'<span class="card-tag">{esc(m["dept"])}</span></div></article>')


def members_json_script():
    """site.js가 모달에 쓸 WHALE_MEMBERS 주입 (홈과 동일 포맷)."""
    data = [{k: m.get(k) for k in ("name", "role", "dept", "color", "initials", "img", "bio", "stats", "soop")}
            for m in MEMBERS]
    # img 경로를 pages/ 기준으로 (../ 접두)
    for d in data:
        if d.get("img"):
            d["img"] = "../" + d["img"]
    return ('<script>window.WHALE_MEMBERS=' +
            json.dumps(data, ensure_ascii=False) + ';</script>')




# ---------- 아키타입: 크루·멤버 ----------

def build_crew():
    ordered = sorted(enumerate(MEMBERS), key=lambda t: (t[1]["rank"], t[0]))
    # 부서 집계
    depts = {}
    for _, m in ordered:
        depts.setdefault(m["dept"], []).append(m["name"])
    dept_cards = "".join(
        f'<div class="dept-card"><div class="dept-count">{len(names)}명</div>'
        f'<h3>{esc(d)}</h3><div class="dept-mem">{esc(" · ".join(names))}</div></div>'
        for d, names in depts.items())

    body = (
        page_head_block("CREW", "고래상사의 사람들", "크루 소개")
        + '<section class="crew-hero img-ani bottom-top">'
          '<div><h2>버추얼 크루 <em>고래상사</em>는<br>16인의 개성으로 굴러갑니다</h2>'
          '<p>사장부터 인턴까지, 회사 역할극이라는 하나의 세계관 안에서 각자의 자리를 맡아 매일 방송을 이어갑니다. '
          '비서·게임·컨텐츠… 부서는 달라도 \'웃음\'이라는 목표는 같습니다.</p>'
          '<div class="crew-metrics">'
          '<div class="crew-metric"><div class="n">16</div><div class="u">크루 인원</div></div>'
          f'<div class="crew-metric"><div class="n">{len(depts)}</div><div class="u">부서</div></div>'
          '<div class="crew-metric"><div class="n">2025</div><div class="u">설립</div></div>'
          '</div></div>'
          '<div class="crew-visual" aria-hidden="true"></div></section>'
        + '<div class="sec03-head" style="padding-left:0;padding-right:0"><div>'
          '<h2 class="img-ani bottom-top" style="font-size:clamp(28px,3.6vw,48px);font-weight:900;letter-spacing:-.03em">'
          '부서 <em style="font-style:normal;color:var(--accent)">구성</em></h2></div>'
          '<a class="more-link" href="members.html">멤버 전체 보기 →</a></div>'
        + f'<div class="dept-grid img-ani bottom-top">{dept_cards}</div>')
    write("crew", "크루 소개", body, PAGE_CSS)


def build_members():
    ordered = sorted(enumerate(MEMBERS), key=lambda t: (t[1]["rank"], t[0]))
    depts = []
    for _, m in ordered:
        if m["dept"] not in depts:
            depts.append(m["dept"])
    chips = ('<button class="chip active" data-f="all">전체</button>'
             + "".join(f'<button class="chip" data-f="{esc(d)}">{esc(d)}</button>' for d in depts))
    cards = "".join(member_card(m, i) for i, m in ordered)
    body = (
        page_head_block("MEMBERS", "고래상사의 사람들", "멤버 목록")
        + f'<div class="pg-tools img-ani bottom-top">{chips}'
          f'<span class="pg-count" id="mCount">전체 {len(MEMBERS)}명</span></div>'
        + f'<div class="mgrid" id="mGrid">{cards}</div>')
    # 부서 필터 (클라이언트)
    filt = """<script>(function(){
  var chips=[].slice.call(document.querySelectorAll('.chip[data-f]'));
  var cards=[].slice.call(document.querySelectorAll('#mGrid .mcard'));
  var count=document.getElementById('mCount');
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('active')});c.classList.add('active');
    var f=c.getAttribute('data-f'),n=0;
    cards.forEach(function(card){
      var show=f==='all'||card.querySelector('.card-tag').textContent===f;
      card.style.display=show?'':'none';if(show)n++;});
    count.textContent=(f==='all'?'전체':f)+' '+n+'명';
  });});
})();</script>"""
    live = """<script>(function(){
  var URL='https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/status.json';
  var grid=document.getElementById('mGrid');
  function apply(map){
    var cards=[].slice.call(grid.querySelectorAll('.mcard'));
    cards.forEach(function(card){
      var id=card.getAttribute('data-soop'),s=map[id];
      var badge=card.querySelector('.mlive');
      if(s&&s.is_live){
        card.classList.add('is-live');
        badge.hidden=false;badge.href=s.live_url||('https://www.sooplive.co.kr/station/'+id);
        badge.querySelector('.mv-n').textContent=(s.viewers||0).toLocaleString();
        card.setAttribute('data-live','1');
      }else{card.classList.remove('is-live');badge.hidden=true;card.removeAttribute('data-live');}
    });
    // 방송중 카드를 앞으로
    cards.sort(function(a,b){return (b.getAttribute('data-live')?1:0)-(a.getAttribute('data-live')?1:0);})
      .forEach(function(c){grid.appendChild(c);});
  }
  // LIVE 뱃지 클릭은 모달 대신 방송으로
  [].forEach.call(grid.querySelectorAll('.mlive'),function(a){
    a.addEventListener('click',function(e){e.stopPropagation();});});
  function load(){fetch(URL+'?v='+Date.now()).then(function(r){return r.json();}).then(function(d){
    var map={};if(d&&d.members){Object.keys(d.members).forEach(function(k){var m=d.members[k];map[m.id]=m;});}
    apply(map);}).catch(function(){});}
  load();setInterval(load,300000);
})();</script>"""
    # 카드 클릭 → 멤버 상세페이지 이동(모달 대신). LIVE 뱃지는 stopPropagation(위 live)으로 방송으로 감.
    nav = """<script>(function(){
  var grid=document.getElementById('mGrid');if(!grid)return;
  [].forEach.call(grid.querySelectorAll('.mcard[data-idx]'),function(c){
    var idx=c.getAttribute('data-idx');
    function go(){location.href='member.html?i='+idx;}
    c.addEventListener('click',go);
    c.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
  });
})();</script>"""
    write("members", "멤버 목록", body, PAGE_CSS,
          scripts=members_json_script() + filt + live + nav)


def build_member():
    """멤버 상세 — ?i=인덱스 로 클라이언트 렌더 (16파일 대신 1파일)."""
    body = (
        page_head_block("PROFILE", "고래상사의 사람들", "멤버 상세")
        + '<div class="mdetail img-ani bottom-top" id="mDetail"></div>')
    render = """<script>(function(){
  var M=window.WHALE_MEMBERS||[];
  var i=parseInt(new URLSearchParams(location.search).get('i')||'0',10);
  if(isNaN(i)||i<0||i>=M.length)i=0;
  var PRM=matchMedia('(prefers-reduced-motion:reduce)').matches;
  var SURL='https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/status.json';
  var STATUS={};  // soop id -> {is_live, viewers, title, live_url}
  function countUp(el,t){if(PRM){el.textContent=t.toLocaleString();return;}
    var s=null;(function step(ts){if(!s)s=ts;var p=Math.min((ts-s)/1200,1);
    el.textContent=Math.floor((1-Math.pow(1-p,3))*t).toLocaleString();
    if(p<1)requestAnimationFrame(step);})(performance.now());}
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  // st.live_url은 외부(status 피드) 값 → http/https만 허용, 아니면 신뢰 URL로 폴백(href javascript: 차단)
  function safeHttp(u,fb){try{var p=new URL(u,location.href);return (p.protocol==='http:'||p.protocol==='https:')?u:fb;}catch(e){return fb;}}
  // soop id는 자체 데이터(members.json)에서 오므로 신뢰됨. encodeURIComponent로만 방어.
  function render(animate){
    var m=M[i];if(!m)return;
    document.title=m.name+' · 고래상사';
    var st=STATUS[m.soop]||{}, live=!!st.is_live, sid=encodeURIComponent(m.soop||'');
    var img=m.img?'<img src="'+esc(m.img)+'" alt="'+esc(m.name)+'" onerror="this.style.display=\\'none\\'">':'';
    // 방송중이면 초상 대신 라이브 임베드(멀티뷰와 동일한 play.sooplive.com/{id}/embed)
    var media = live
      ? '<div class="media-live"><div class="embed">'+
          '<span class="live-tag"><span class="d"></span>LIVE '+esc((st.viewers||0).toLocaleString())+'명</span>'+
          '<iframe src="https://play.sooplive.com/'+sid+'/embed" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen scrolling="no" title="'+esc(m.name)+' 방송"></iframe>'+
        '</div>'+(st.title?'<div class="live-title">'+esc(st.title)+'</div>':'')+'</div>'
      : '<div class="portrait" style="background:'+esc(m.color)+'">'+img+'<div class="ava-ph">'+esc(m.initials)+'</div></div>';
    // SOOP 버튼: 방송중=방송으로 / 아니면=방송국으로
    var soopHref = live ? safeHttp(st.live_url, 'https://play.sooplive.co.kr/'+sid)
                        : ('https://www.sooplive.co.kr/station/'+sid);
    var soopBtn = '<a class="btn sm '+(live?'primary':'')+'" href="'+esc(soopHref)+'" target="_blank" rel="noopener">'+
                  (live?'▶ 방송 보러가기':'SOOP 방송국 →')+'</a>';
    var stats=(m.stats||[]).map(function(s,k){
      return '<div class="stat"><div class="n" id="ds'+k+'">0</div><div class="u">'+esc(s.u)+'</div></div>';}).join('');
    var el=document.getElementById('mDetail');
    el.innerHTML= media +
      '<div><div class="dept-label">'+esc(m.dept)+'</div>'+
        '<h2>'+esc(m.name)+'</h2><div class="role">'+esc(m.role)+'</div>'+
        '<p class="bio">'+esc(m.bio)+'</p>'+
        '<div class="stats">'+stats+'</div>'+
        '<div class="soop-row">'+soopBtn+'</div>'+
        '<div class="navrow"><button class="btn sm" id="dPrev">← 이전 멤버</button>'+
        '<button class="btn sm" id="dNext">다음 멤버 →</button>'+
        '<a class="btn sm" href="members.html">전체 목록</a></div></div>';
    (m.stats||[]).forEach(function(s,k){var e=document.getElementById('ds'+k);if(!e)return;
      animate?countUp(e,s.n):(e.textContent=s.n.toLocaleString());});
    document.getElementById('dPrev').onclick=function(){i=(i-1+M.length)%M.length;render(true);};
    document.getElementById('dNext').onclick=function(){i=(i+1)%M.length;render(true);};
  }
  render(true);  // 즉시 페인트(초상). 상태 도착 후 방송중이면 임베드로 갱신
  fetch(SURL+'?v='+Date.now()).then(function(r){return r.json();}).then(function(d){
    if(d&&d.members)Object.keys(d.members).forEach(function(k){var m=d.members[k];STATUS[m.id]=m;});
  }).catch(function(){}).then(function(){render(false);});
})();</script>"""
    write("member", "멤버 상세", body, PAGE_CSS,
          scripts=members_json_script() + render)


# ---------- 아키타입: 클립 (Firebase 실시간 CRUD, 공지 구현 패턴 그대로 적용) ----------

CLIP_CATEGORIES = ["예능", "합방", "토크", "게임", "대회", "일상"]


def clip_form_modal():
    """클립 작성/수정 공용 모달 (목록·상세 페이지 공통 삽입)."""
    cat_opts = "".join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in CLIP_CATEGORIES)
    return f"""<div class="n-modal-bg" id="clModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="clModalTitle">
  <div class="n-modal">
    <button class="n-modal-close" id="clModalClose" type="button" aria-label="닫기">×</button>
    <h2 id="clModalTitle">클립 추가</h2>
    <form id="clForm" novalidate>
      <label class="field"><span>카테고리</span>
        <select name="category">{cat_opts}</select></label>
      <label class="field"><span>제목</span><input type="text" name="title" maxlength="120" required></label>
      <label class="field"><span>제작자</span><input type="text" name="creator" maxlength="60" required></label>
      <label class="field"><span>설명 (선택)</span><textarea name="desc" rows="4"></textarea></label>
      <label class="field"><span>영상 URL (선택)</span><input type="url" name="url" placeholder="https://..."></label>
      <label class="field"><span>이미지 URL (선택, 비우면 영상 링크로 미리보기 · 둘 다 없으면 그라데이션)</span><input type="url" name="img" placeholder="https://..."></label>
      <label class="field"><span>태그 (쉼표로 구분 · 같은 태그의 아카이브 상세에 이 클립이 표시됨)</span><input type="text" name="tags" placeholder="예: 크루대전, 여름특집"></label>
      <label class="n-pin-field" id="clFeatField" style="display:none">
        <input type="checkbox" name="featured"><span>대표 클립으로 지정 (관리자만, 기존 대표는 자동 해제)</span></label>
      <p class="n-modal-msg" id="clModalMsg" role="status" aria-live="polite"></p>
      <button class="btn primary" type="submit">저장</button>
    </form>
  </div>
</div>"""


# 목록/상세 양쪽에서 공유하는 CRUD 헬퍼 JS — 공지의 _NOTICE_JS_SHARED와 동일한 구조.
_CLIP_JS_SHARED = """
  var U=window.WhaleUI, D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  // href에 넣기 전 스킴 검증: http/https만 허용(javascript:/data:/vbscript: 등 차단).
  function safeUrl(u){u=(u==null?'':String(u)).trim();return /^https?:\\/\\//i.test(u)?u:'#';}
  function fmtViews(n){n=n||0;return n>=10000?(n/10000).toFixed(1)+'만':n.toLocaleString();}
  // 쉼표 구분 문자열 <-> 태그 배열 (아카이브와 연결하는 키. 대소문자 무시 매칭은 소비측에서 처리)
  function parseTags(s){return (s||'').split(',').map(function(x){return x.trim();}).filter(Boolean);}
  function bgOf(c){
    return c.img?'<img src="'+esc(c.img)+'" alt="'+esc(c.title)+'" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover" onerror="this.style.display=\\'none\\'">'
      :'<div style="position:absolute;inset:0;background:'+esc(c.grad||'linear-gradient(135deg,#0f1730,#2f63ff)')+'"></div>';
  }
  var clModalBg=document.getElementById('clModalBg'), clModalTitle=document.getElementById('clModalTitle'),
      clForm=document.getElementById('clForm'), clFeatField=document.getElementById('clFeatField'),
      clModalMsg=document.getElementById('clModalMsg');
  var clMode='create', clItem=null, clOnSaved=function(){};
  function clOpenForm(mode,item,cb){
    clMode=mode;clItem=item;clOnSaved=cb||function(){};
    clModalMsg.textContent='';clForm.reset();
    clModalTitle.textContent=mode==='edit'?'클립 수정':'클립 추가';
    if(clFeatField)clFeatField.style.display=U.isAdmin()?'flex':'none';
    if(mode==='edit'&&item){
      clForm.category.value=item.category||'예능';clForm.title.value=item.title||'';
      clForm.creator.value=item.creator||'';clForm.desc.value=item.desc||'';
      clForm.url.value=item.url||'';clForm.img.value=item.img||'';
      clForm.tags.value=(item.tags||[]).join(', ');
      if(clForm.featured)clForm.featured.checked=!!item.featured;
    } else if(clForm.featured){clForm.featured.checked=false;}
    clModalBg.hidden=false;
  }
  function clCloseForm(){clModalBg.hidden=true;}
  var clModalCloseBtn=document.getElementById('clModalClose');
  if(clModalCloseBtn)clModalCloseBtn.addEventListener('click',clCloseForm);
  if(clModalBg)clModalBg.addEventListener('click',function(e){if(e.target===clModalBg)clCloseForm();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&clModalBg&&!clModalBg.hidden)clCloseForm();});
  function unsetOtherFeatured(keepId){
    return D.list('clips').then(function(items){
      var others=items.filter(function(c){return c.id!==keepId&&c.featured;});
      var chain=Promise.resolve();
      others.forEach(function(c){chain=chain.then(function(){return D.update('clips',c.id,{featured:false});});});
      return chain;
    });
  }
  if(clForm)clForm.addEventListener('submit',function(e){
    e.preventDefault();
    var title=clForm.title.value.trim(), creator=clForm.creator.value.trim(), category=clForm.category.value;
    if(!title||!creator){clModalMsg.textContent='제목·제작자를 입력하세요.';return;}
    var payload={category:category,title:title,creator:creator,desc:clForm.desc.value.trim(),
      url:clForm.url.value.trim(),img:clForm.img.value.trim(),tags:parseTags(clForm.tags.value)};
    if(payload.url&&!/^https?:\\/\\//i.test(payload.url)){clModalMsg.textContent='영상 URL은 http:// 또는 https:// 로 시작해야 합니다.';return;}
    if(payload.img&&!/^https?:\\/\\//i.test(payload.img)){clModalMsg.textContent='이미지 URL은 http:// 또는 https:// 로 시작해야 합니다.';return;}
    var wantFeatured=!!(clForm.featured&&clForm.featured.checked&&U.isAdmin());
    if(U.isAdmin())payload.featured=wantFeatured;
    clModalMsg.textContent='저장 중...';
    var save=(clMode==='edit'&&clItem)?D.update('clips',clItem.id,payload):D.create('clips',payload);
    save.then(function(saved){
      if(!wantFeatured)return null;
      var myId=(clMode==='edit'&&clItem)?clItem.id:(saved&&saved.name);
      return unsetOtherFeatured(myId);
    }).then(function(){clCloseForm();clOnSaved();})
      .catch(function(err){clModalMsg.textContent='저장 실패: '+(err&&err.message||err);});
  });
"""


def build_clips():
    """클립 갤러리 (clips) — WhaleData.list('clips')로 런타임 로드, Firebase 실시간 CRUD.
    대표 클립 히어로 + 카테고리 필터 + 카드 그리드는 목록 도착 후 클라이언트에서 렌더."""
    body = (
        page_head_block("CLIPS", "베스트 클립", "베스트 클립")
        + '<div class="n-actions img-ani bottom-top" id="cActions"></div>'
        + '<div id="cHero" class="img-ani bottom-top"></div>'
        + '<div class="pg-tools img-ani bottom-top" id="cChips"></div>'
        + '<div class="cgrid img-ani bottom-top" id="cGrid">불러오는 중...</div>'
        + clip_form_modal())

    js = "<script>(function(){" + _CLIP_JS_SHARED + """
  var hero=document.getElementById('cHero'), grid=document.getElementById('cGrid'),
      chipsWrap=document.getElementById('cChips'), actionsEl=document.getElementById('cActions');
  var ALL=[], activeFilter='all';

  function renderActions(){
    var html='';
    if(U.isLoggedIn())html+='<button type="button" class="btn sm primary" id="clWriteBtn">+ 클립 추가</button>';
    if(U.isAdmin()&&!ALL.length)html+='<button type="button" class="btn sm" id="clImportBtn">운영 아카이브에서 클립 불러오기 (최초 1회)</button>';
    actionsEl.innerHTML=html;
    var wb=document.getElementById('clWriteBtn');if(wb)wb.addEventListener('click',function(){clOpenForm('create',null,reload);});
    var ib=document.getElementById('clImportBtn');if(ib)ib.addEventListener('click',importClips);
  }
  /* 운영 /contests의 videos 중 라벨에 '클립'/'편집'이 든 것만 골라 일괄 등록 (§2.5-4).
     클릭 시점의 운영 데이터를 그대로 읽으므로 cutover 직전 추가분도 포함됨.
     tags에 대회 제목을 넣어둠 — 아카이브 기록에 같은 태그를 달면 상세의 '관련 클립'으로 연결. */
  function importClips(){
    if(!U.isAdmin())return;
    if(!confirm('운영 아카이브의 클립 영상만 골라 등록합니다. 계속할까요?'))return;
    fetch('https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/contests.json?v='+Date.now())
      .then(function(r){return r.json();}).then(function(d){
        d=d||{};
        var found=[];
        Object.keys(d).forEach(function(k){
          var o=d[k]||{}, vids=(o.videos||[]).filter(function(v){
            var lab=(v.label||'');return lab.indexOf('클립')>=0||lab.indexOf('편집')>=0;});
          vids.forEach(function(v,i){
            var suffix=(v.label&&v.label!=='클립')?' '+v.label:' 클립';
            if(vids.length>1)suffix+=' '+(i+1);
            found.push({category:'대회', title:(o.title||'')+suffix, creator:'고래상사',
              desc:o.date||'', url:v.url||'', img:'',
              tags:(o.tags&&o.tags.length)?o.tags:(o.title?[o.title]:[])});
          });
        });
        if(!found.length){alert('불러올 클립 영상이 없습니다.');return;}
        if(!confirm(found.length+'개의 클립을 등록합니다. 진행할까요?'))return;
        var chain=Promise.resolve();
        found.forEach(function(p){chain=chain.then(function(){return D.create('clips',p);});});
        chain.then(function(){alert('클립 '+found.length+'개 등록 완료.');reload();})
             .catch(function(err){alert('등록 중 오류: '+(err&&err.message||err));reload();});
      }).catch(function(err){alert('운영 기록 불러오기 실패: '+(err&&err.message||err));});
  }
  function heroActionsHtml(c){
    var h='';
    if(U.isAdmin())h+='<button type="button" class="n-btn'+(c.featured?' pin-on':'')+'" data-act="feat" data-id="'+esc(c.id)+'">'+(c.featured?'★ 대표 해제':'☆ 대표 지정')+'</button>';
    if(U.canEdit(c)){
      h+='<button type="button" class="n-btn" data-act="edit" data-id="'+esc(c.id)+'">✏️ 수정</button>';
      h+='<button type="button" class="n-btn del" data-act="del" data-id="'+esc(c.id)+'">🗑 삭제</button>';
    }
    return h?'<span class="n-row-actions">'+h+'</span>':'';
  }
  function renderHero(){
    if(!ALL.length){hero.innerHTML='';return;}
    var feat=ALL.filter(function(c){return c.featured;})[0]||ALL[0];
    hero.innerHTML='<section class="clips-hero">'
      +'<a class="orig-feat" href="clip.html?id='+encodeURIComponent(feat.id)+'" aria-label="'+esc(feat.title)+' 시청">'
      +bgOf(feat)+'<div class="orig-play" aria-hidden="true">▶</div></a>'
      +'<div class="clips-hero-info">'
      +heroActionsHtml(feat)
      +'<div class="ch-cat">'+esc(feat.category||'')+' · 대표 클립</div>'
      +'<p class="ch-title">'+esc(feat.title)+'</p>'
      +'<div class="ch-meta"><span>제작: '+esc(feat.creator)+'</span>'
      +(feat.date?'<span>'+esc(feat.date)+'</span>':'')
      +(feat.duration?'<span class="ch-dur">'+esc(feat.duration)+'</span>':'')
      +'<span>'+fmtViews(feat.views)+' 조회</span></div>'
      +(feat.desc?'<p class="ch-desc">'+esc(feat.desc)+'</p>':'')
      +'<a class="btn primary" href="clip.html?id='+encodeURIComponent(feat.id)+'">▶ 클립 시청</a>'
      +'</div></section>';
  }
  function renderChips(){
    var cats=[];ALL.forEach(function(c){if(c.category&&cats.indexOf(c.category)<0)cats.push(c.category);});
    var html='<button type="button" class="chip'+(activeFilter==='all'?' active':'')+'" data-f="all">전체</button>'
      +cats.map(function(c){return '<button type="button" class="chip'+(activeFilter===c?' active':'')+'" data-f="'+esc(c)+'">'+esc(c)+'</button>';}).join('')
      +'<span class="pg-count" id="cCount"></span>';
    chipsWrap.innerHTML=html;
    [].slice.call(chipsWrap.querySelectorAll('.chip')).forEach(function(c){
      c.addEventListener('click',function(){activeFilter=c.getAttribute('data-f');renderChips();renderGrid();});
    });
  }
  function cardActionsHtml(c){
    var h='';
    if(U.isAdmin())h+='<button type="button" class="n-btn'+(c.featured?' pin-on':'')+'" data-act="feat" data-id="'+esc(c.id)+'">'+(c.featured?'★ 해제':'☆ 대표')+'</button>';
    if(U.canEdit(c)){
      h+='<button type="button" class="n-btn" data-act="edit" data-id="'+esc(c.id)+'">✏️</button>';
      h+='<button type="button" class="n-btn del" data-act="del" data-id="'+esc(c.id)+'">🗑</button>';
    }
    return h?'<div class="ccard-actions n-row-actions">'+h+'</div>':'';
  }
  function card(c){
    return '<article class="ccard img-ani bottom-top" data-id="'+esc(c.id)+'" data-cat="'+esc(c.category||'')+'" role="button" tabindex="0" aria-label="'+esc(c.title)+' 클립 시청">'
      +(c.featured?'<span class="ccard-feat">★ 대표</span>':'')
      +'<div class="ccard-thumb">'+bgOf(c)+'<div class="cplay" aria-hidden="true">▶</div></div>'
      +'<div class="ccard-info"><div class="ccard-title">'+esc(c.title)+'</div>'
      +'<div class="ccard-meta"><span>'+esc(c.creator)+'</span>'
      +(c.duration?'<span class="ccard-dur">'+esc(c.duration)+'</span>':'')
      +'<span>'+fmtViews(c.views)+' 조회</span></div></div>'
      +cardActionsHtml(c)+'</article>';
  }
  function renderGrid(){
    var filtered=activeFilter==='all'?ALL:ALL.filter(function(c){return c.category===activeFilter;});
    var count=document.getElementById('cCount');
    if(count)count.textContent=(activeFilter==='all'?'전체':activeFilter)+' '+filtered.length+'개';
    grid.innerHTML=filtered.length?filtered.map(card).join(''):'<div class="nlist-msg" style="grid-column:1/-1">'+(ALL.length?'해당 분류의 클립이 없습니다.':'등록된 클립이 없습니다.')+'</div>';
  }
  function reload(){
    return D.list('clips').then(function(items){
      ALL=items;renderActions();renderHero();renderChips();renderGrid();
    }).catch(function(err){
      grid.innerHTML='<div class="nlist-msg" style="grid-column:1/-1">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
    });
  }
  function toggleFeatured(item){
    var next=!item.featured;
    var p=next?unsetOtherFeatured(item.id).then(function(){return D.update('clips',item.id,{featured:true});})
      :D.update('clips',item.id,{featured:false});
    p.then(reload).catch(function(err){alert('처리 실패: '+(err&&err.message||err));});
  }
  function removeClip(item){
    if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
    D.remove('clips',item.id).then(reload).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
  }
  function handleAction(e){
    var btn=e.target.closest&&e.target.closest('[data-act]');
    if(!btn)return false;
    e.stopPropagation();
    var id=btn.getAttribute('data-id'),act=btn.getAttribute('data-act');
    var item=ALL.filter(function(x){return x.id===id;})[0];
    if(!item)return true;
    if(act==='feat')toggleFeatured(item);
    else if(act==='edit')clOpenForm('edit',item,reload);
    else if(act==='del')removeClip(item);
    return true;
  }
  hero.addEventListener('click',function(e){handleAction(e);});
  grid.addEventListener('click',function(e){
    if(handleAction(e))return;
    var art=e.target.closest&&e.target.closest('.ccard');
    if(art)location.href='clip.html?id='+encodeURIComponent(art.getAttribute('data-id'));
  });
  grid.addEventListener('keydown',function(e){
    if(e.key!=='Enter'&&e.key!==' ')return;
    var art=e.target.closest&&e.target.closest('.ccard');
    if(art&&e.target===art)location.href='clip.html?id='+encodeURIComponent(art.getAttribute('data-id'));
  });
  document.addEventListener('whale:authchange',reload);  // 로그인/로그아웃 시 버튼 재렌더
  reload();
})();</script>"""

    write("clips", "베스트 클립", body, PAGE_CSS, scripts=js)


def build_clip():
    """클립 시청 상세 (clip) — WhaleData.list('clips')로 런타임 로드. ?id=Firebase키, 옛 ?i=인덱스는 폴백."""
    body = (
        page_head_block("CLIPS", "베스트 클립", "클립 시청")
        + '<div class="cdetail img-ani bottom-top" id="cDetail"></div>'
        + clip_form_modal())

    js = "<script>(function(){" + _CLIP_JS_SHARED + """
  var detail=document.getElementById('cDetail');
  var qs=new URLSearchParams(location.search), id=qs.get('id'), legacyIdx=qs.get('i');
  var C=[], idx=0;
  function load(){
    return D.list('clips').then(function(items){
      C=items;
      if(id){
        idx=C.findIndex(function(c){return c.id===id;});
        if(idx<0)idx=0;
      } else if(legacyIdx!=null&&!isNaN(parseInt(legacyIdx,10))){
        idx=Math.min(Math.max(parseInt(legacyIdx,10),0),Math.max(C.length-1,0));
      } else idx=0;
      render();
    }).catch(function(err){
      detail.innerHTML='<div class="nlist-msg">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
    });
  }
  function render(){
    var c=C[idx];
    if(!c){
      detail.innerHTML='<div class="nlist-msg">등록된 클립이 없습니다.<br><a class="btn sm" href="clips.html">전체 클립</a></div>';
      return;
    }
    id=c.id;
    document.title=c.title+' · 고래상사';
    if(history.replaceState)history.replaceState(null,'','clip.html?id='+encodeURIComponent(c.id));
    var rel=[];
    C.forEach(function(r,j){if(j!==idx&&rel.length<5)rel.push(j);});
    var relHtml=rel.map(function(j){
      return '<li><a class="orig-item" href="clip.html?id='+encodeURIComponent(C[j].id)+'" data-j="'+j+'">'
        +'<span class="oi-t">'+esc(C[j].title)+'</span><span class="oi-ar">↗</span></a></li>';
    }).join('');
    var manage='';
    if(U.isAdmin())manage+='<button class="btn sm'+(c.featured?' primary':'')+'" id="cDetFeat" type="button">'+(c.featured?'★ 대표 해제':'☆ 대표 지정')+'</button>';
    if(U.canEdit(c)){
      manage+='<button class="btn sm" id="cDetEdit" type="button">✏️ 수정</button>';
      manage+='<button class="btn sm" id="cDetDel" type="button">🗑 삭제</button>';
    }
    detail.innerHTML=
      '<div class="cdetail-player">'+bgOf(c)+'<div class="orig-play" aria-hidden="true">▶</div></div>'
      +'<div class="cm-cat">'+esc(c.category||'')+'</div>'
      +'<h2 class="cdetail-title">'+esc(c.title)+'</h2>'
      +'<div class="cdetail-meta"><span>제작: '+esc(c.creator)+'</span>'
      +(c.date?'<span>'+esc(c.date)+'</span>':'')
      +(c.duration?'<span class="ccard-dur">'+esc(c.duration)+'</span>':'')
      +'<span>'+fmtViews(c.views)+' 조회</span></div>'
      +(c.desc?'<p class="cdetail-desc">'+esc(c.desc)+'</p>':'')
      +(c.url?'<div style="margin:0 0 20px"><a class="btn sm primary" href="'+esc(safeUrl(c.url))+'" target="_blank" rel="noopener">▶ 원본 영상 보기</a></div>':'')
      +'<div class="cdetail-nav"><button class="btn sm" id="cPrev">← 이전 클립</button>'
      +'<button class="btn sm" id="cNext">다음 클립 →</button>'
      +manage
      +'<a class="btn sm primary" href="clips.html">전체 클립</a></div>'
      +(relHtml?'<div class="crelated-head">관련 클립</div><ul class="orig-list">'+relHtml+'</ul>':'');
    document.getElementById('cPrev').onclick=function(){idx=(idx-1+C.length)%C.length;render();};
    document.getElementById('cNext').onclick=function(){idx=(idx+1)%C.length;render();};
    [].forEach.call(detail.querySelectorAll('.orig-item[data-j]'),function(a){
      a.onclick=function(e){e.preventDefault();idx=parseInt(this.getAttribute('data-j'),10);render();};
    });
    var featBtn=document.getElementById('cDetFeat');
    if(featBtn)featBtn.onclick=function(){
      var next=!c.featured;
      var p=next?unsetOtherFeatured(c.id).then(function(){return D.update('clips',c.id,{featured:true});})
        :D.update('clips',c.id,{featured:false});
      p.then(load).catch(function(err){alert('처리 실패: '+(err&&err.message||err));});
    };
    var editBtn=document.getElementById('cDetEdit');
    if(editBtn)editBtn.onclick=function(){clOpenForm('edit',c,load);};
    var delBtn=document.getElementById('cDetDel');
    if(delBtn)delBtn.onclick=function(){
      if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
      D.remove('clips',c.id).then(function(){location.href='clips.html';}).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
    };
  }
  document.addEventListener('whale:authchange',load);  // 로그인/로그아웃 시 관리 버튼 재렌더
  load();
})();</script>"""

    write("clip", "클립 시청", body, PAGE_CSS, scripts=js)


# ---------- 아카이브 추가 CSS (PAGE_CSS 위에 얹는 아카이브 전용 레이아웃) ----------

ARCHIVE_CSS = PAGE_CSS + """
/* 아카이브 그리드 — 가로형 2열 (클립 4열 수직카드와 차별화) */
.agrid{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(12px,1.6vw,18px);
  margin-top:clamp(24px,3vw,36px)}
@media(max-width:900px){.agrid{grid-template-columns:1fr}}
/* 아카이브 로우 (가로: 썸네일 + 정보) */
.arow{display:flex;gap:14px;align-items:flex-start;
  background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:14px;cursor:pointer;
  transition:border-color .3s var(--ease),box-shadow .3s var(--ease),transform .3s var(--ease)}
.arow:hover{border-color:var(--brand);box-shadow:0 10px 30px rgba(47,99,255,.25);transform:translateY(-3px)}
.arow-thumb{position:relative;aspect-ratio:16/9;width:clamp(100px,14vw,164px);flex-shrink:0;
  border-radius:10px;overflow:hidden;background:#0f1730}
.arow-thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  transition:transform .4s var(--ease)}
.arow:hover .arow-thumb img{transform:scale(1.06)}
.arow-grad{position:absolute;inset:0}
.aplay{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:30px;height:22px;border-radius:6px;background:#ff0033;color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:10px;z-index:2;
  box-shadow:0 4px 14px rgba(0,0,0,.5);
  transition:transform .2s var(--ease),background .2s var(--ease)}
.arow:hover .aplay{transform:translate(-50%,-50%) scale(1.1);background:#ff1f4b}
.arow-info{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px}
.arow-type{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.1em;
  color:var(--accent);text-transform:uppercase;padding:2px 8px;
  border:1px solid rgba(15,181,176,.35);border-radius:999px;width:fit-content;margin-bottom:1px}
.arow-title{font-size:13.5px;font-weight:800;letter-spacing:-.02em;line-height:1.35;
  word-break:keep-all;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.arow-cast{font-size:11.5px;color:var(--ink-2)}
.arow-meta{font-size:11px;color:var(--ink-2);display:flex;gap:6px;flex-wrap:wrap}
.arow-dur{color:var(--accent);font-weight:700}
.arow .btn{margin-top:4px;align-self:flex-start}
/* 아카이브 상세 */
.adetail-player{aspect-ratio:16/9;border-radius:16px;overflow:hidden;background:#0f1730;
  position:relative;border:1px solid var(--line);box-shadow:var(--shadow);margin-bottom:22px}
.adetail-title{font-size:clamp(20px,2.8vw,36px);font-weight:900;letter-spacing:-.03em;
  line-height:1.25;margin:0 0 12px;word-break:keep-all}
.adetail-meta{font-size:13px;color:var(--ink-2);display:flex;flex-wrap:wrap;
  gap:6px 16px;margin-bottom:14px}
.adetail-desc{font-size:clamp(15px,1.4vw,17px);color:var(--ink-2);line-height:1.75;
  margin:0 0 22px;word-break:keep-all}
.adetail-nav{display:flex;gap:10px;margin-bottom:36px;flex-wrap:wrap}
/* 크루대전 기록 (실데이터) */
.ct-card{display:block;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px;
  cursor:pointer;transition:border-color .25s,transform .25s,box-shadow .25s}
.ct-card:hover{border-color:var(--brand);transform:translateY(-3px);box-shadow:0 12px 34px rgba(47,99,255,.25)}
.ct-top{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.ct-rank{font-size:12px;font-weight:900;padding:4px 10px;border-radius:999px;letter-spacing:.02em}
.ct-rank.win{background:color-mix(in srgb,var(--warn) 90%,#000);color:#1a1400}
.ct-rank.lose{background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line-2)}
.ct-cat{font-size:12px;font-weight:900;padding:4px 10px;border-radius:999px;letter-spacing:.02em;
  background:color-mix(in srgb,var(--accent) 20%,transparent);color:var(--accent);border:1px solid rgba(15,181,176,.35)}
.ct-date{font-size:12.5px;color:var(--ink-2);font-family:'JetBrains Mono',monospace;margin-left:auto}
.ct-title{font-size:clamp(16px,1.8vw,20px);font-weight:800;letter-spacing:-.02em;line-height:1.35;word-break:keep-all;margin-bottom:12px}
.ct-meta{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:12.5px;color:var(--ink-2)}
.ct-wl{font-weight:800}.ct-wl .w{color:var(--accent)}.ct-wl .l{color:var(--hot)}
.ct-cast{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px}
.ct-chip{font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;background:rgba(255,255,255,.08);color:var(--ink-2)}
/* 상세 */
.cd-games{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin:8px 0 26px}
.cd-game{display:flex;align-items:center;justify-content:space-between;gap:10px;background:var(--surface);
  border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:14px;font-weight:700}
.cd-res{font-size:11px;font-weight:900;padding:3px 9px;border-radius:6px}
.cd-res.w{background:color-mix(in srgb,var(--accent) 22%,transparent);color:var(--accent)}
.cd-res.l{background:color-mix(in srgb,var(--hot) 20%,transparent);color:var(--hot)}
.cd-vids{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 26px}
.cd-opp{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.cd-opp .op{font-size:13px;font-weight:700;padding:6px 12px;border-radius:10px;border:1px solid var(--line-2);background:var(--surface-2)}
.cd-h{font-size:16px;font-weight:900;margin:0 0 12px;letter-spacing:-.01em}
/* 관련 클립 (태그 매칭) — 아카이브 상세에 임베드 미리보기 그리드 */
.rc-count{font-size:12px;font-weight:800;color:var(--ink-2);vertical-align:middle;margin-left:4px}
.rc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px;margin:6px 0 30px}
.rc-card{display:flex;flex-direction:column;gap:6px;background:var(--surface);border:1px solid var(--line);
  border-radius:12px;overflow:hidden;transition:border-color .25s,transform .25s,box-shadow .25s}
.rc-card:hover{border-color:var(--brand);transform:translateY(-3px);box-shadow:0 10px 28px rgba(47,99,255,.22)}
.rc-media{position:relative;aspect-ratio:16/9;background:#0f1730;display:block}
.rc-media iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.rc-static{display:flex;align-items:center;justify-content:center;overflow:hidden}
.rc-static img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .4s var(--ease)}
.rc-card:hover .rc-static img{transform:scale(1.06)}
.rc-play{width:34px;height:24px;border-radius:6px;background:#ff0033;color:#fff;display:flex;
  align-items:center;justify-content:center;font-size:11px;z-index:1}
.rc-t{font-size:13px;font-weight:800;letter-spacing:-.02em;line-height:1.35;word-break:keep-all;
  padding:0 12px;margin-top:4px;color:var(--ink);text-decoration:none;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.rc-t:hover{color:var(--brand)}
.rc-by{font-size:11.5px;color:var(--ink-2);padding:0 12px 12px}
"""


# ---------- 아카이브 데이터 JSON 주입 ----------

def archive_json_script():
    """pages/ 기준 WHALE_ARCHIVE 주입 (아카이브 상세 페이지용)."""
    data = []
    for a in ARCHIVE:
        d = dict(a)
        if d.get("img"):
            d["img"] = "../" + d["img"]
        data.append(d)
    return ('<script>window.WHALE_ARCHIVE=' +
            json.dumps(data, ensure_ascii=False) + ';</script>')


# ---------- 아카이브: 통합 목록 + 상세 (Firebase 실시간 CRUD, 클립/일정과 동일 패턴 + isAdmin 게이팅) ----------

def archive_form_modal():
    """대회 기록 작성/수정 공용 모달 (목록·상세 페이지 공통 삽입). 관리자 전용."""
    return """<div class="n-modal-bg" id="acModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="acModalTitle">
  <div class="n-modal">
    <button class="n-modal-close" id="acModalClose" type="button" aria-label="닫기">×</button>
    <h2 id="acModalTitle">기록 추가</h2>
    <form id="acForm" novalidate>
      <label class="field"><span>분류</span>
        <select name="category"><option value="크루대전">크루대전</option><option value="컨텐츠">컨텐츠</option></select></label>
      <label class="field"><span>제목</span><input type="text" name="title" maxlength="120" required></label>
      <label class="field"><span>날짜</span><input type="text" name="date" maxlength="20" placeholder="예: 2026.06.01"></label>
      <label class="field crewonly"><span>순위 (숫자, 1=우승, 비우면 '참가'로 표시)</span><input type="number" name="rank" min="1" step="1"></label>
      <label class="field"><span>참여 멤버 (쉼표로 구분)</span><input type="text" name="members" placeholder="예: 울산큰고래, 김마렌"></label>
      <label class="field crewonly"><span>상대 크루 (한 줄에 하나, "이름|승" 또는 "이름|패")</span>
        <textarea name="opponents" rows="4" placeholder="블랙팀|승
화이트팀|패"></textarea></label>
      <label class="field crewonly"><span>게임 결과 (한 줄에 하나, "게임명|승" 또는 "게임명|패")</span>
        <textarea name="games" rows="4" placeholder="족구|승
줄다리기|패"></textarea></label>
      <label class="field"><span>영상 (한 줄에 하나, "URL|라벨", http/https만 허용)</span>
        <textarea name="videos" rows="3" placeholder="https://youtu.be/xxxx|풀영상"></textarea></label>
      <label class="field"><span>태그 (쉼표로 구분 · 같은 태그를 가진 클립이 이 상세에 '관련 클립'으로 표시됨)</span>
        <input type="text" name="tags" placeholder="예: 크루대전, 여름특집"></label>
      <p class="n-modal-msg" id="acModalMsg" role="status" aria-live="polite"></p>
      <button class="btn primary" type="submit">저장</button>
    </form>
  </div>
</div>"""


# 목록/상세 양쪽에서 공유하는 CRUD 헬퍼 JS — 클립/일정의 _..._JS_SHARED와 동일 구조.
# 아카이브는 canEdit(본인 여부)이 아니라 isAdmin() 하나로만 게이팅한다(요구사항).
# opponents.result: true=='승'(고래상사가 이김) — 운영 admin.js 저장 규약(isWin)·실데이터 15건 검증(07-11)과 일치.
# (07-11 이전 렌더가 반대로 해석해 우승 기록 5건이 '패'로 표시되던 버그를 수정. 폼 파스/직렬화도 동일 규약.)
# games.result: 렌더 규칙상 true=='승', false=='패' — 기존 렌더 로직(wl 집계·cd-res 클래스) 그대로 유지.
_ARCHIVE_JS_SHARED = r"""
  var U=window.WhaleUI, D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function safeUrl(u){u=(u==null?'':String(u)).trim();return /^https?:\/\//i.test(u)?u:'#';}
  function wl(c){var w=0,l=0,g=c.games||{};Object.keys(g).forEach(function(k){g[k].result?w++:l++;});return {w:w,l:l};}
  function parseMembers(s){return (s||'').split(',').map(function(x){return x.trim();}).filter(Boolean);}
  /* 승/패 표기가 없거나 오타면 null 반환 → 제출부에서 안내 (조용한 오저장 방지) */
  function parseOpponents(s){
    var out=[], lines=(s||'').split('\n').map(function(l){return l.trim();}).filter(Boolean);
    for(var i=0;i<lines.length;i++){
      var parts=lines[i].split('|'), name=(parts[0]||'').trim(), tag=(parts[1]||'').trim();
      if(!name)continue;
      if(tag!=='승'&&tag!=='패')return null;
      out.push({name:name, result: tag==='승'});
    }
    return out;
  }
  function parseGames(s){
    var out={}, lines=(s||'').split('\n').map(function(l){return l.trim();}).filter(Boolean);
    for(var i=0;i<lines.length;i++){
      var parts=lines[i].split('|'), name=(parts[0]||'').trim(), tag=(parts[1]||'').trim();
      if(!name)continue;
      if(tag!=='승'&&tag!=='패')return null;
      out['game'+i]={name:name, result: tag==='승'};
    }
    return out;
  }
  function parseVideos(s){
    var lines=(s||'').split('\n').map(function(l){return l.trim();}).filter(Boolean), out=[];
    for(var i=0;i<lines.length;i++){
      var parts=lines[i].split('|'), url=(parts[0]||'').trim(), label=(parts[1]||'').trim();
      if(!url)continue;
      if(!/^https?:\/\//i.test(url))return null;
      out.push({url:url, label: label||'영상'});
    }
    return out;
  }
  function serializeOpponents(arr){return (arr||[]).map(function(o){return (o.name||'')+'|'+(o.result?'승':'패');}).join('\n');}
  function serializeGames(obj){
    var keys=Object.keys(obj||{});
    return keys.map(function(k){var g=obj[k]||{};return (g.name||'')+'|'+(g.result?'승':'패');}).join('\n');
  }
  function serializeVideos(arr){return (arr||[]).map(function(v){return (v.url||'')+'|'+(v.label||'');}).join('\n');}

  var acModalBg=document.getElementById('acModalBg'), acModalTitle=document.getElementById('acModalTitle'),
      acForm=document.getElementById('acForm'), acModalMsg=document.getElementById('acModalMsg');
  var acMode='create', acItem=null, acOnSaved=function(){};
  // 분류=컨텐츠면 크루대전 전용 필드(순위/상대/게임)를 숨긴다.
  function toggleCrew(){
    var isCrew=(acForm.category.value||'크루대전')==='크루대전';
    [].forEach.call(acForm.querySelectorAll('.crewonly'),function(el){el.style.display=isCrew?'':'none';});
  }
  if(acForm)acForm.category.addEventListener('change',toggleCrew);
  function acOpenForm(mode,item,cb){
    if(!U.isAdmin())return;
    acMode=mode;acItem=item;acOnSaved=cb||function(){};
    acModalMsg.textContent='';acForm.reset();
    acModalTitle.textContent=mode==='edit'?'기록 수정':'기록 추가';
    if(mode==='edit'&&item){
      acForm.category.value=item.category||'크루대전';
      acForm.title.value=item.title||'';acForm.date.value=item.date||'';
      acForm.rank.value=(item.rank!=null?item.rank:'');
      acForm.members.value=(item.members||[]).join(', ');
      acForm.opponents.value=serializeOpponents(item.opponents);
      acForm.games.value=serializeGames(item.games);
      acForm.videos.value=serializeVideos(item.videos);
      acForm.tags.value=(item.tags||[]).join(', ');
    }
    toggleCrew();
    acModalBg.hidden=false;
  }
  function acCloseForm(){acModalBg.hidden=true;}
  var acModalCloseBtn=document.getElementById('acModalClose');
  if(acModalCloseBtn)acModalCloseBtn.addEventListener('click',acCloseForm);
  if(acModalBg)acModalBg.addEventListener('click',function(e){if(e.target===acModalBg)acCloseForm();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&acModalBg&&!acModalBg.hidden)acCloseForm();});
  if(acForm)acForm.addEventListener('submit',function(e){
    e.preventDefault();
    if(!U.isAdmin()){acModalMsg.textContent='관리자만 저장할 수 있습니다.';return;}
    var title=acForm.title.value.trim();
    if(!title){acModalMsg.textContent='대회명을 입력하세요.';return;}
    var videos=parseVideos(acForm.videos.value);
    if(videos===null){acModalMsg.textContent='영상 URL은 http:// 또는 https:// 로 시작해야 합니다.';return;}
    var category=acForm.category.value||'크루대전';
    var isCrew=category==='크루대전';
    var rankVal=acForm.rank.value.trim();
    var opponents=isCrew?parseOpponents(acForm.opponents.value):[];
    if(opponents===null){acModalMsg.textContent='상대 크루는 한 줄에 "이름|승" 또는 "이름|패" 형식으로 입력하세요.';return;}
    var games=isCrew?parseGames(acForm.games.value):{};
    if(games===null){acModalMsg.textContent='게임 결과는 한 줄에 "게임명|승" 또는 "게임명|패" 형식으로 입력하세요.';return;}
    var payload={
      category:category,
      title:title, date:acForm.date.value.trim(),
      rank: (isCrew&&rankVal!=='')?parseInt(rankVal,10):null,
      members: parseMembers(acForm.members.value),
      opponents: opponents,
      games: games,
      videos: videos,
      tags: parseMembers(acForm.tags.value)
    };
    acModalMsg.textContent='저장 중...';
    var p=(acMode==='edit'&&acItem)?D.update('contests',acItem.id,payload):D.create('contests',payload);
    p.then(function(){acCloseForm();acOnSaved();}).catch(function(err){acModalMsg.textContent='저장 실패: '+(err&&err.message||err);});
  });
"""


def build_archive():
    """통합 아카이브 — WhaleData.list('contests')로 /rework/contests 실시간 로드.
    분류(category=크루대전|컨텐츠) 칩으로 필터. 크루대전은 순위/전적, 컨텐츠는 순위·전적 없이 표시.
    관리자는 +기록 추가/수정/삭제 가능, 비어있을 때 운영 /contests.json에서 1회 이관하는 '불러오기' 버튼도 제공."""
    body = (page_head_block("ARCHIVE", "콘텐츠 아카이브", "통합 아카이브")
            + '<div class="n-actions img-ani bottom-top" id="aActions"></div>'
            + '<div class="pg-tools img-ani bottom-top">'
              '<button class="chip active" data-f="all">전체</button>'
              '<button class="chip" data-f="크루대전">🏆 크루대전</button>'
              '<button class="chip" data-f="컨텐츠">🎬 컨텐츠</button>'
              '<span class="pg-count" id="aCount"></span></div>'
            + '<div class="agrid img-ani bottom-top" id="aGrid">'
              '<div class="stub" style="grid-column:1/-1"><p>대회 기록을 불러오는 중…</p></div></div>'
            + archive_form_modal())
    js = "<script>(function(){" + _ARCHIVE_JS_SHARED + r"""
  var grid=document.getElementById('aGrid'), count=document.getElementById('aCount'), actionsEl=document.getElementById('aActions');
  var all=[], filt='all';
  function renderActions(){
    var html='';
    if(U.isAdmin())html+='<button type="button" class="btn sm primary" id="acWriteBtn">+ 기록 추가</button>';
    if(U.isAdmin()&&!all.length)html+='<button type="button" class="btn sm" id="acSeedBtn">불러오기 (운영 기록 이관, 최초 1회)</button>';
    actionsEl.innerHTML=html;
    var wb=document.getElementById('acWriteBtn'); if(wb)wb.addEventListener('click',function(){acOpenForm('create',null,reload);});
    var sb=document.getElementById('acSeedBtn'); if(sb)sb.addEventListener('click',importSeed);
  }
  function rowActionsHtml(c){
    if(!U.isAdmin())return '';
    return '<div class="n-row-actions" style="margin-top:10px">'
      +'<button type="button" class="n-btn" data-act="edit" data-id="'+esc(c.id)+'">✏️ 수정</button>'
      +'<button type="button" class="n-btn del" data-act="del" data-id="'+esc(c.id)+'">🗑 삭제</button></div>';
  }
  function card(c){
    var isCrew=(c.category||'크루대전')==='크루대전';
    var r=wl(c),win=c.rank===1;
    var cast=(c.members||[]).slice(0,6).map(function(m){return '<span class="ct-chip">'+esc(m)+'</span>';}).join('');
    var more=(c.members||[]).length>6?'<span class="ct-chip">+'+((c.members||[]).length-6)+'</span>':'';
    var badge=isCrew
      ? '<span class="ct-rank '+(win?'win':'lose')+'">'+(win?'🏆 우승':(c.rank?c.rank+'위':'참가'))+'</span>'
      : '<span class="ct-cat">🎬 컨텐츠</span>';
    var meta=isCrew
      ? '<div class="ct-meta"><span class="ct-wl">전적 <span class="w">'+r.w+'승</span> <span class="l">'+r.l+'패</span></span></div>'
      : '';
    return '<div class="ct-card" data-id="'+esc(c.id)+'" role="button" tabindex="0" aria-label="'+esc(c.title||'기록')+' 상세 보기">'
      +'<div class="ct-top">'+badge
      +'<span class="ct-date">'+esc(c.date||'')+'</span></div>'
      +'<div class="ct-title">'+esc(c.title||'제목 없음')+'</div>'
      +meta
      +'<div class="ct-cast">'+cast+more+'</div>'
      +rowActionsHtml(c)+'</div>';
  }
  function render(){
    var arr=all.filter(function(c){
      if(filt==='all')return true;
      return (c.category||'크루대전')===filt;});
    count.textContent=arr.length+'건';
    grid.innerHTML=arr.length?arr.map(card).join(''):'<div class="stub" style="grid-column:1/-1"><p>해당 기록이 없습니다.</p></div>';
  }
  function reload(){
    return D.list('contests').then(function(items){
      all=items.slice().sort(function(a,b){return ((a.date||'')<(b.date||'')?1:(a.date||'')>(b.date||'')?-1:0);});
      renderActions();render();
    }).catch(function(err){
      grid.innerHTML='<div class="stub" style="grid-column:1/-1"><p>불러오기 실패: '+esc(err&&err.message||err)+'</p></div>';
    });
  }
  [].forEach.call(document.querySelectorAll('.chip[data-f]'),function(c){c.addEventListener('click',function(){
    document.querySelectorAll('.chip[data-f]').forEach(function(x){x.classList.remove('active')});
    c.classList.add('active');filt=c.getAttribute('data-f');render();});});
  function removeRecord(item){
    if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
    D.remove('contests',item.id).then(reload).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
  }
  grid.addEventListener('click',function(e){
    var btn=e.target.closest&&e.target.closest('[data-act]');
    if(btn){
      e.stopPropagation();
      var id=btn.getAttribute('data-id'), act=btn.getAttribute('data-act');
      var item=all.filter(function(x){return x.id===id;})[0];
      if(!item)return;
      if(act==='edit')acOpenForm('edit',item,reload);
      else if(act==='del')removeRecord(item);
      return;
    }
    var card=e.target.closest&&e.target.closest('.ct-card');
    if(card)location.href='archive-detail.html?id='+encodeURIComponent(card.getAttribute('data-id'));
  });
  grid.addEventListener('keydown',function(e){
    if(e.key!=='Enter'&&e.key!==' ')return;
    var card=e.target.closest&&e.target.closest('.ct-card');
    if(card&&e.target===card){e.preventDefault();location.href='archive-detail.html?id='+encodeURIComponent(card.getAttribute('data-id'));}
  });
  function importSeed(){
    if(!U.isAdmin())return;
    if(!confirm('운영 대회 기록을 관리용 저장소로 1회 이관합니다. 계속할까요?'))return;
    fetch('https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/contests.json?v='+Date.now())
      .then(function(r){return r.json();}).then(function(d){
        d=d||{};
        var keys=Object.keys(d);
        if(!keys.length){alert('불러올 운영 기록이 없습니다.');return;}
        var chain=Promise.resolve();
        keys.forEach(function(k){
          chain=chain.then(function(){
            var o=d[k]||{};
            return D.create('contests',{
              title:o.title||'', date:o.date||'', rank:(o.rank!=null?o.rank:null),
              members:o.members||[], opponents:o.opponents||[], games:o.games||{}, videos:o.videos||[]
            });
          });
        });
        chain.then(function(){alert('이관 완료.');reload();}).catch(function(err){alert('이관 중 오류: '+(err&&err.message||err));reload();});
      }).catch(function(err){alert('운영 기록 불러오기 실패: '+(err&&err.message||err));});
  }
  document.addEventListener('whale:authchange',reload);  // 로그인/로그아웃 시 버튼 재렌더
  reload();
})();</script>"""
    write("archive", "크루대전 기록", body, ARCHIVE_CSS, scripts=js)


def build_archive_detail():
    """기록 상세 (크루대전/컨텐츠 공용) — WhaleData.list('contests') 후 ?id=로 find (클립 상세 패턴과 동일).
    분류=컨텐츠면 순위·상대·게임 섹션은 표시하지 않음. 태그가 겹치는 클립을 '관련 클립'으로 임베드."""
    body = (page_head_block("ARCHIVE", "콘텐츠 아카이브", "기록 상세")
            + '<div class="img-ani bottom-top" id="cDetail"><div class="stub"><p>불러오는 중…</p></div></div>'
            + archive_form_modal())
    js = "<script>(function(){" + _ARCHIVE_JS_SHARED + r"""
  var el=document.getElementById('cDetail');
  var id=new URLSearchParams(location.search).get('id');
  var cur=null, allClips=[];
  // 영상 URL -> 임베드(미리보기) URL. 운영본 contest.js getEmbedUrl 규칙 이식.
  // ⚠️보안: 부분일치(indexOf)는 evil.com/sooplive.com 류 우회가 되므로 new URL로 호스트를
  // 엄격 검증(정확일치 또는 .접미사)하고, 원본을 그대로 넘기지 않고 검증된 조각으로 재조립한다.
  function hostMatch(h,d){return h===d||h.slice(-(d.length+1))==='.'+d;}
  function embedUrlOf(u){
    var pu;
    try{pu=new URL((u==null?'':String(u)).trim());}catch(e){return null;}
    if(pu.protocol!=='https:'&&pu.protocol!=='http:')return null;
    var host=pu.hostname.toLowerCase();
    // YouTube — 검증된 videoId(문자/숫자/-/_)로만 재조립
    if(hostMatch(host,'youtu.be')){
      var sid=pu.pathname.replace(/^\/+/,'').split('/')[0];
      return /^[\w-]{6,}$/.test(sid)?'https://www.youtube.com/embed/'+sid:null;
    }
    if(hostMatch(host,'youtube.com')||hostMatch(host,'youtube-nocookie.com')){
      var vid=pu.searchParams.get('v');
      if(!vid){var me=pu.pathname.match(/^\/embed\/([\w-]{6,})/);if(me)vid=me[1];}
      return (vid&&/^[\w-]{6,}$/.test(vid))?'https://www.youtube.com/embed/'+vid:null;
    }
    // SOOP VOD — 숫자 player id로만 재조립(원본 패스스루 금지)
    if(hostMatch(host,'sooplive.com')||hostMatch(host,'sooplive.co.kr')){
      var pm=pu.pathname.match(/\/player\/(\d+)/);
      if(pm)return 'https://'+host+'/player/'+pm[1]+'/embed';
      if(/\/embed(\/|$)/.test(pu.pathname))return 'https://'+host+pu.pathname;
    }
    return null;
  }
  function tagsOf(x){return (x&&x.tags)||[];}
  function relatedOf(contest){
    var ct=tagsOf(contest).map(function(t){return String(t).toLowerCase();});
    if(!ct.length)return [];
    return allClips.filter(function(cl){
      return tagsOf(cl).some(function(t){return ct.indexOf(String(t).toLowerCase())>=0;});
    });
  }
  function renderRelated(){
    var rel=relatedOf(cur);
    if(!rel.length)return '';
    var cards=rel.map(function(cl){
      var emb=embedUrlOf(cl.url);
      var media = emb
        ? '<div class="rc-media"><iframe src="'+esc(emb)+'" loading="lazy" allowfullscreen allow="autoplay; encrypted-media; picture-in-picture" title="'+esc(cl.title||'클립')+'"></iframe></div>'
        : '<a class="rc-media rc-static" href="clip.html?id='+encodeURIComponent(cl.id)+'">'
            +(cl.img?'<img src="'+esc(safeUrl(cl.img))+'" alt="'+esc(cl.title||'')+'" loading="lazy" onerror="this.style.display=\'none\'">':'<span class="rc-play">▶</span>')
          +'</a>';
      return '<div class="rc-card">'+media
        +'<a class="rc-t" href="clip.html?id='+encodeURIComponent(cl.id)+'">'+esc(cl.title||'클립')+'</a>'
        +(cl.creator?'<span class="rc-by">'+esc(cl.creator)+'</span>':'')+'</div>';
    }).join('');
    return '<h3 class="cd-h" style="margin-top:26px">관련 클립 <span class="rc-count">'+rel.length+'</span></h3><div class="rc-grid">'+cards+'</div>';
  }
  function load(){
    if(!id){el.innerHTML='<div class="stub"><p>잘못된 접근입니다.</p><a class="btn primary" href="archive.html">목록으로</a></div>';return Promise.resolve();}
    return Promise.all([D.list('contests'), D.list('clips').catch(function(){return [];})]).then(function(res){
      var items=res[0]||[]; allClips=res[1]||[];
      cur=items.filter(function(x){return x.id===id;})[0];
      render();
    }).catch(function(err){
      el.innerHTML='<div class="stub"><p>불러오지 못했습니다: '+esc(err&&err.message||err)+'</p></div>';
    });
  }
  function render(){
    var c=cur;
    if(!c){el.innerHTML='<div class="stub"><p>기록을 찾을 수 없습니다.</p><a class="btn primary" href="archive.html">목록으로</a></div>';return;}
    document.title=(c.title||'기록 상세')+' · 고래상사';
    var isCrew=(c.category||'크루대전')==='크루대전';
    var win=c.rank===1;
    var g=c.games||{},games=Object.keys(g).map(function(k){var x=g[k];
      return '<div class="cd-game"><span>'+esc(x.name)+'</span><span class="cd-res '+(x.result?'w':'l')+'">'+(x.result?'승':'패')+'</span></div>';}).join('');
    var opp=(c.opponents||[]).map(function(o){return '<span class="op">'+esc(o.name)+(o.result===true?' <span style=color:var(--accent)>승</span>':o.result===false?' <span style=color:var(--hot)>패</span>':'')+'</span>';}).join('');
    var vids=(c.videos||[]).map(function(v){return '<a class="btn sm primary" href="'+esc(safeUrl(v.url))+'" target="_blank" rel="noopener">▶ '+esc(v.label||'영상')+'</a>';}).join('');
    var cast=(c.members||[]).map(function(m){return '<span class="ct-chip">'+esc(m)+'</span>';}).join('');
    var manage='';
    if(U.isAdmin()){
      manage='<button class="btn sm" id="cDetEdit" type="button">✏️ 수정</button>'
        +'<button class="btn sm" id="cDetDel" type="button">🗑 삭제</button>';
    }
    el.innerHTML=
      '<div class="ct-top" style="margin-bottom:14px">'
        +(isCrew?'<span class="ct-rank '+(win?'win':'lose')+'">'+(win?'🏆 우승':(c.rank?c.rank+'위':'참가'))+'</span>':'<span class="ct-cat">🎬 컨텐츠</span>')
        +'<span class="ct-date">'+esc(c.date||'')+'</span></div>'
      +'<h2 class="adetail-title">'+esc(c.title||'')+'</h2>'
      +(vids?'<div class="cd-vids">'+vids+'</div>':'')
      +(opp?'<h3 class="cd-h">상대 크루</h3><div class="cd-opp">'+opp+'</div>':'')
      +(games?'<h3 class="cd-h" style="margin-top:22px">경기 결과</h3><div class="cd-games">'+games+'</div>':'')
      +'<h3 class="cd-h">참가 멤버</h3><div class="ct-cast" style="margin-bottom:26px">'+cast+'</div>'
      +(c.notes?'<p class="adetail-desc">'+esc(c.notes)+'</p>':'')
      +renderRelated()
      +'<div class="adetail-nav">'+manage+'<a class="btn sm primary" href="archive.html">← 전체 기록</a></div>';
    var editBtn=document.getElementById('cDetEdit');
    if(editBtn)editBtn.onclick=function(){acOpenForm('edit',c,load);};
    var delBtn=document.getElementById('cDetDel');
    if(delBtn)delBtn.onclick=function(){
      if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
      D.remove('contests',c.id).then(function(){location.href='archive.html';}).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
    };
  }
  document.addEventListener('whale:authchange',load);  // 로그인/로그아웃 시 관리 버튼 재렌더
  load();
})();</script>"""
    write("archive-detail", "대회 상세", body, ARCHIVE_CSS, scripts=js)


# ---------- 아키타입: 방송 일정 (월 캘린더) ----------

SCHEDULE_CSS = PAGE_CSS + """
.sview{display:flex;gap:8px;margin-bottom:clamp(20px,3vw,32px)}
.cal{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:clamp(14px,2vw,24px)}
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.cal-title{font-size:clamp(18px,2.4vw,26px);font-weight:900;letter-spacing:-.02em}
.cal-nav button{width:40px;height:40px;border-radius:10px;border:1px solid var(--line-2);background:var(--surface-2);color:var(--ink);font-size:18px;cursor:pointer;transition:.15s}
.cal-nav button:hover{border-color:var(--brand);background:var(--brand)}
.cal-dow{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-bottom:6px}
.cal-dow span{text-align:center;font-size:12px;font-weight:800;color:var(--ink-2);padding:4px 0}
.cal-dow span:first-child{color:var(--hot)}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.cal-cell{min-height:96px;border:1px solid var(--line);border-radius:10px;padding:6px;background:rgba(255,255,255,.02);display:flex;flex-direction:column;gap:3px;overflow:hidden}
.cal-cell.empty{background:transparent;border-color:transparent}
.cal-cell.today{border-color:var(--brand);box-shadow:inset 0 0 0 1px var(--brand)}
.cal-dnum{font-size:12px;font-weight:700;color:var(--ink-2)}
.cal-cell.today .cal-dnum{color:var(--brand)}
.cal-ev{font-size:11px;font-weight:700;line-height:1.25;padding:3px 6px;border-radius:6px;cursor:pointer;
  border-left:3px solid var(--tc);background:color-mix(in srgb,var(--tc) 18%,transparent);color:var(--ink);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:background .15s}
.cal-ev:hover{background:color-mix(in srgb,var(--tc) 34%,transparent)}
.cal-more{font-size:10.5px;color:var(--ink-2);font-weight:700;padding-left:3px}
.slist{display:flex;flex-direction:column}
.slist .sched-row{cursor:pointer;transition:transform .15s}
.slist .sched-row:hover{transform:translateX(6px)}
.slist .sched-row .day{--tc:var(--brand);background:var(--tc)}
.stype{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.04em;padding:2px 7px;border-radius:999px;margin-left:8px;
  border-left:0;background:color-mix(in srgb,var(--tc) 22%,transparent);color:var(--ink)}
.sdetail-meta{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:14px 0 22px;color:var(--ink-2);font-size:14px}
.sdetail-cast{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}
.sdetail-cast .mchip{font-size:13px;font-weight:700;padding:7px 13px;border-radius:999px;border:1px solid var(--line-2);background:var(--surface-2)}
.sdetail-desc{font-size:clamp(15px,1.4vw,17px);color:#c3cee6;line-height:1.75;margin-bottom:26px;word-break:keep-all}
.sdetail-nav{display:flex;gap:10px}
@media(max-width:640px){.cal-cell{min-height:70px}.cal-ev{font-size:10px}}
"""

# 타입 -> 솔리드 색 (칩/배지 틴트 기준)
TYPE_COLORS = {
    "개인방송": "#2f63ff", "합방": "#0fb5b0", "대회": "#ff4d4d",
    "특집": "#ffcb45", "공지방송": "#8b5cf6",
}




def schedule_form_modal():
    """일정 작성/수정 공용 모달 (캘린더·상세 페이지 공통 삽입)."""
    type_opts = "".join(f'<option value="{esc(t)}">{esc(t)}</option>' for t in TYPE_COLORS)
    return f"""<div class="n-modal-bg" id="scModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="scModalTitle">
  <div class="n-modal">
    <button class="n-modal-close" id="scModalClose" type="button" aria-label="닫기">×</button>
    <h2 id="scModalTitle">일정 추가</h2>
    <form id="scForm" novalidate>
      <label class="field"><span>날짜</span><input type="date" name="date" required></label>
      <label class="field"><span>시간</span><input type="time" name="time" required></label>
      <label class="field"><span>제목</span><input type="text" name="title" maxlength="120" required></label>
      <label class="field"><span>유형</span><select name="type">{type_opts}</select></label>
      <label class="field"><span>참여 멤버 (쉼표로 구분)</span><input type="text" name="members" placeholder="예: 김마렌, 조아라"></label>
      <label class="field"><span>설명 (선택)</span><textarea name="desc" rows="4"></textarea></label>
      <p class="n-modal-msg" id="scModalMsg" role="status" aria-live="polite"></p>
      <button class="btn primary" type="submit">저장</button>
    </form>
  </div>
</div>"""


# 목록/상세 양쪽에서 공유하는 CRUD 헬퍼 JS — 공지의 _NOTICE_JS_SHARED와 동일한 구조.
# 일정에는 pinned/featured 같은 관리자 전용 플래그가 없다 — canEdit(admin은 항상 true)만으로 충분.
_SCHEDULE_JS_SHARED = ("""
  var U=window.WhaleUI, D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var TC=""" + json.dumps(TYPE_COLORS, ensure_ascii=False) + """;
  function tcOf(t){return TC[t]||'#2f63ff';}
  function sortSchedules(arr){
    return arr.slice().sort(function(a,b){
      var ka=(a.date||'')+' '+(a.time||''), kb=(b.date||'')+' '+(b.time||'');
      return ka<kb?-1:(ka>kb?1:0);
    });
  }
  var scModalBg=document.getElementById('scModalBg'), scModalTitle=document.getElementById('scModalTitle'),
      scForm=document.getElementById('scForm'), scModalMsg=document.getElementById('scModalMsg');
  var scMode='create', scItem=null, scOnSaved=function(){};
  function scOpenForm(mode,item,cb){
    scMode=mode;scItem=item;scOnSaved=cb||function(){};
    scModalMsg.textContent='';scForm.reset();
    scModalTitle.textContent=mode==='edit'?'일정 수정':'일정 추가';
    if(mode==='edit'&&item){
      scForm.date.value=item.date||'';scForm.time.value=item.time||'';scForm.title.value=item.title||'';
      scForm.type.value=item.type||'개인방송';scForm.members.value=(item.members||[]).join(', ');
      scForm.desc.value=item.desc||'';
    } else {
      scForm.date.value=new Date().toISOString().slice(0,10);
    }
    scModalBg.hidden=false;
  }
  function scCloseForm(){scModalBg.hidden=true;}
  var scModalCloseBtn=document.getElementById('scModalClose');
  if(scModalCloseBtn)scModalCloseBtn.addEventListener('click',scCloseForm);
  if(scModalBg)scModalBg.addEventListener('click',function(e){if(e.target===scModalBg)scCloseForm();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&scModalBg&&!scModalBg.hidden)scCloseForm();});
  if(scForm)scForm.addEventListener('submit',function(e){
    e.preventDefault();
    var date=scForm.date.value, time=scForm.time.value, title=scForm.title.value.trim(), type=scForm.type.value;
    if(!date||!time||!title){scModalMsg.textContent='날짜·시간·제목을 모두 입력하세요.';return;}
    var members=scForm.members.value.split(',').map(function(s){return s.trim();}).filter(Boolean);
    var payload={date:date,time:time,title:title,type:type,members:members,desc:scForm.desc.value.trim()};
    scModalMsg.textContent='저장 중...';
    var p=(scMode==='edit'&&scItem)?D.update('schedules',scItem.id,payload):D.create('schedules',payload);
    p.then(function(){scCloseForm();scOnSaved();}).catch(function(err){scModalMsg.textContent='저장 실패: '+(err&&err.message||err);});
  });
""")


def build_schedule():
    """방송 일정 (schedules) — WhaleData.list('schedules')로 런타임 로드, Firebase 실시간 CRUD.
    캘린더 셀은 클릭 시 상세로만 이동(편집 버튼 없음), 목록 뷰 각 행에 canEdit이면 수정/삭제 버튼 노출."""
    body = (
        page_head_block("SCHEDULE", "방송 일정", "일정 캘린더")
        + '<div class="n-actions img-ani bottom-top" id="scActions"></div>'
        + '<div class="pg-tools img-ani bottom-top"><div class="sview">'
          '<button class="chip active" data-v="cal">📅 달력</button>'
          '<button class="chip" data-v="list">☰ 목록</button></div></div>'
        + '<div id="calView" class="img-ani bottom-top"><div class="cal">'
          '<div class="cal-nav"><button id="calPrev" aria-label="이전 달">‹</button>'
          '<div class="cal-title" id="calTitle"></div>'
          '<button id="calNext" aria-label="다음 달">›</button></div>'
          '<div class="cal-dow"><span>일</span><span>월</span><span>화</span><span>수</span>'
          '<span>목</span><span>금</span><span>토</span></div>'
          '<div class="cal-grid" id="calGrid"></div></div></div>'
        + '<div id="listView" class="slist img-ani bottom-top" style="display:none"></div>'
        + schedule_form_modal())

    js = "<script>(function(){" + _SCHEDULE_JS_SHARED + """
  var S=[];
  var actionsEl=document.getElementById('scActions');
  var now=new Date();
  var cur=new Date(now.getFullYear(),now.getMonth(),1);
  var todayISO=(function(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);})();
  var grid=document.getElementById('calGrid'),title=document.getElementById('calTitle');
  var lv=document.getElementById('listView');
  function iso(y,m,d){return y+'-'+('0'+(m+1)).slice(-2)+'-'+('0'+d).slice(-2);}
  function renderActions(){
    var html='';
    if(U.isLoggedIn())html+='<button type="button" class="btn sm primary" id="scWriteBtn">+ 일정 추가</button>';
    actionsEl.innerHTML=html;
    var wb=document.getElementById('scWriteBtn');if(wb)wb.addEventListener('click',function(){scOpenForm('create',null,reload);});
  }
  function evChip(e){
    return '<div class="cal-ev" style="--tc:'+tcOf(e.type)+'" role="button" tabindex="0" '
      +'data-id="'+esc(e.id)+'" title="'+esc(e.time)+' '+esc(e.title)+'">'+esc(e.title)+'</div>';
  }
  function renderCal(){
    var byDate={};S.forEach(function(e){(byDate[e.date]=byDate[e.date]||[]).push(e);});
    var y=cur.getFullYear(),m=cur.getMonth();
    title.textContent=y+'년 '+(m+1)+'월';
    var first=new Date(y,m,1).getDay(),days=new Date(y,m+1,0).getDate();
    var h='';for(var b=0;b<first;b++)h+='<div class="cal-cell empty"></div>';
    for(var d=1;d<=days;d++){
      var key=iso(y,m,d),evs=byDate[key]||[];
      var cls='cal-cell'+(key===todayISO?' today':'');
      var inner='<div class="cal-dnum">'+d+'</div>';
      evs.slice(0,2).forEach(function(e){inner+=evChip(e);});
      if(evs.length>2)inner+='<div class="cal-more">+'+(evs.length-2)+' 더보기</div>';
      h+='<div class="'+cls+'">'+inner+'</div>';
    }
    grid.innerHTML=h;
    [].forEach.call(grid.querySelectorAll('.cal-ev'),function(el){
      var go=function(){location.href='schedule-detail.html?id='+encodeURIComponent(el.getAttribute('data-id'));};
      el.addEventListener('click',go);
      el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
    });
  }
  function rowActionsHtml(e){
    var h='';
    if(U.canEdit(e)){
      h+='<button type="button" class="n-btn" data-act="edit" data-id="'+esc(e.id)+'">✏️ 수정</button>';
      h+='<button type="button" class="n-btn del" data-act="del" data-id="'+esc(e.id)+'">🗑 삭제</button>';
    }
    return h?'<span class="n-row-actions">'+h+'</span>':'';
  }
  function renderList(){
    var sorted=sortSchedules(S);
    var W=['일','월','화','수','목','금','토'];
    if(!sorted.length){lv.innerHTML='<div class="nlist-msg">등록된 일정이 없습니다.</div>';return;}
    lv.innerHTML=sorted.map(function(e){
      var dt=new Date(e.date+'T00:00:00');
      var badge=(e.date.slice(5).replace('-','.'))+' ('+W[dt.getDay()]+')';
      var cast=(e.members||[]).join(', ');
      return '<div class="sched-row" data-id="'+esc(e.id)+'" role="button" tabindex="0">'
        +'<span class="day" style="--tc:'+tcOf(e.type)+';background:'+tcOf(e.type)+'">'+badge+'</span>'
        +'<span class="desc"><b>'+esc(e.time)+'</b> — '+esc(e.title)
        +'<span class="stype" style="--tc:'+tcOf(e.type)+'">'+esc(e.type)+'</span>'
        +'<br><span style="color:var(--ink-2);font-size:12.5px">'+esc(cast)+'</span></span>'
        +rowActionsHtml(e)+'</div>';
    }).join('');
  }
  function reload(){
    return D.list('schedules').then(function(items){
      S=items;renderActions();renderCal();renderList();
    }).catch(function(err){
      grid.innerHTML='<div class="nlist-msg">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
      lv.innerHTML='';
    });
  }
  function removeSchedule(item){
    if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
    D.remove('schedules',item.id).then(reload).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
  }
  function handleAction(e){
    var btn=e.target.closest&&e.target.closest('[data-act]');
    if(!btn)return false;
    e.stopPropagation();
    var id=btn.getAttribute('data-id'),act=btn.getAttribute('data-act');
    var item=S.filter(function(x){return x.id===id;})[0];
    if(!item)return true;
    if(act==='edit')scOpenForm('edit',item,reload);
    else if(act==='del')removeSchedule(item);
    return true;
  }
  lv.addEventListener('click',function(e){
    if(handleAction(e))return;
    var row=e.target.closest&&e.target.closest('.sched-row');
    if(row)location.href='schedule-detail.html?id='+encodeURIComponent(row.getAttribute('data-id'));
  });
  lv.addEventListener('keydown',function(e){
    if(e.key!=='Enter'&&e.key!==' ')return;
    var row=e.target.closest&&e.target.closest('.sched-row');
    if(row&&e.target===row)location.href='schedule-detail.html?id='+encodeURIComponent(row.getAttribute('data-id'));
  });
  document.getElementById('calPrev').onclick=function(){cur.setMonth(cur.getMonth()-1);renderCal();};
  document.getElementById('calNext').onclick=function(){cur.setMonth(cur.getMonth()+1);renderCal();};
  // 뷰 토글
  var chips=[].slice.call(document.querySelectorAll('.sview .chip'));
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('active')});c.classList.add('active');
    var v=c.getAttribute('data-v');
    document.getElementById('calView').style.display=v==='cal'?'':'none';
    lv.style.display=v==='list'?'':'none';
  });});
  document.addEventListener('whale:authchange',reload);  // 로그인/로그아웃 시 버튼 재렌더
  reload();
})();</script>"""
    write("schedule", "일정 캘린더", body, SCHEDULE_CSS, scripts=js)


def build_schedule_detail():
    """일정 상세 — WhaleData.list('schedules')로 런타임 로드. ?id=Firebase키, 옛 ?i=인덱스는 폴백."""
    body = (page_head_block("SCHEDULE", "방송 일정", "일정 상세")
            + '<div class="img-ani bottom-top" id="sDetail"></div>'
            + schedule_form_modal())
    js = "<script>(function(){" + _SCHEDULE_JS_SHARED + """
  var detail=document.getElementById('sDetail');
  var qs=new URLSearchParams(location.search), id=qs.get('id'), legacyIdx=qs.get('i');
  var S=[], idx=0;
  var W=['일','월','화','수','목','금','토'];
  function load(){
    return D.list('schedules').then(function(items){
      S=sortSchedules(items);
      if(id){
        idx=S.findIndex(function(e){return e.id===id;});
        if(idx<0)idx=0;
      } else if(legacyIdx!=null&&!isNaN(parseInt(legacyIdx,10))){
        idx=Math.min(Math.max(parseInt(legacyIdx,10),0),Math.max(S.length-1,0));
      } else idx=0;
      render();
    }).catch(function(err){
      detail.innerHTML='<div class="nlist-msg">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
    });
  }
  function render(){
    var e=S[idx];
    if(!e){
      detail.innerHTML='<div class="nlist-msg">등록된 일정이 없습니다.<br><a class="btn sm" href="schedule.html">전체 일정</a></div>';
      return;
    }
    id=e.id;
    document.title=e.title+' · 고래상사';
    if(history.replaceState)history.replaceState(null,'','schedule-detail.html?id='+encodeURIComponent(e.id));
    var dt=new Date(e.date+'T00:00:00');
    var dateStr=e.date.replace(/-/g,'.')+' ('+W[dt.getDay()]+') '+e.time;
    var cast=(e.members||[]).map(function(m){return '<span class="mchip">'+esc(m)+'</span>';}).join('');
    var rel=S.filter(function(x){return x.id!==e.id&&(x.type===e.type||x.date===e.date);}).slice(0,4);
    var relH=rel.map(function(x){
      return '<li><a class="orig-item" href="schedule-detail.html?id='+encodeURIComponent(x.id)+'">'
        +'<span class="oi-t">'+esc(x.date.slice(5).replace('-','.'))+' · '+esc(x.title)+'</span>'
        +'<span class="oi-ar" aria-hidden="true">↗</span></a></li>';}).join('');
    var manage='';
    if(U.canEdit(e)){
      manage+='<button class="btn sm" id="sDetEdit" type="button">✏️ 수정</button>';
      manage+='<button class="btn sm" id="sDetDel" type="button">🗑 삭제</button>';
    }
    document.getElementById('sDetail').innerHTML=
      '<div class="cm-cat" style="color:'+tcOf(e.type)+'">'+esc(e.type)+'</div>'
      +'<h2 class="adetail-title" style="font-size:clamp(28px,4vw,52px);font-weight:900;letter-spacing:-.03em;margin:6px 0 0">'+esc(e.title)+'</h2>'
      +'<div class="sdetail-meta"><span>🗓 '+esc(dateStr)+'</span></div>'
      +'<div class="sdetail-cast">'+cast+'</div>'
      +(e.desc?'<p class="sdetail-desc">'+esc(e.desc)+'</p>':'')
      +'<div class="sdetail-nav"><button class="btn sm" id="sPrev">← 이전 일정</button>'
      +'<button class="btn sm" id="sNext">다음 일정 →</button>'
      +manage
      +'<a class="btn sm primary" href="schedule.html">전체 일정</a></div>'
      +(relH?'<div class="crelated-head" style="margin-top:40px;font-weight:900;font-size:18px">관련 일정</div><ul class="orig-list">'+relH+'</ul>':'');
    document.getElementById('sPrev').onclick=function(){idx=(idx-1+S.length)%S.length;render();};
    document.getElementById('sNext').onclick=function(){idx=(idx+1)%S.length;render();};
    var editBtn=document.getElementById('sDetEdit');
    if(editBtn)editBtn.onclick=function(){scOpenForm('edit',e,load);};
    var delBtn=document.getElementById('sDetDel');
    if(delBtn)delBtn.onclick=function(){
      if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
      D.remove('schedules',e.id).then(function(){location.href='schedule.html';}).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
    };
  }
  document.addEventListener('whale:authchange',load);  // 로그인/로그아웃 시 관리 버튼 재렌더
  load();
})();</script>"""
    write("schedule-detail", "일정 상세", body, SCHEDULE_CSS, scripts=js)


# ---------- 아키타입: 공지 ----------

NOTICE_CSS = PAGE_CSS + """
.nlist{display:flex;flex-direction:column;gap:10px}
.nrow{display:flex;align-items:center;gap:14px;padding:18px 20px;border:1px solid var(--line);border-radius:12px;
  background:var(--surface);cursor:pointer;transition:border-color .2s,transform .2s,background .2s}
.nrow:hover{border-color:var(--brand);transform:translateX(4px);background:var(--surface-2)}
.ncat{flex:0 0 auto;font-size:11px;font-weight:800;letter-spacing:.04em;padding:4px 10px;border-radius:999px;
  border-left:3px solid var(--tc);background:color-mix(in srgb,var(--tc) 20%,transparent);color:var(--ink)}
.npin{color:var(--warn);font-size:13px;flex:0 0 auto}
.ntitle{flex:1 1 auto;font-size:clamp(15px,1.5vw,18px);font-weight:700;letter-spacing:-.01em;word-break:keep-all}
.ndate{flex:0 0 auto;font-size:12.5px;color:var(--ink-2);font-family:'JetBrains Mono',monospace}
.narrow{flex:0 0 auto;color:var(--ink-2);transition:color .2s}
.nrow:hover .narrow{color:var(--accent)}
.ndetail-cat{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.04em;padding:5px 12px;border-radius:999px;
  border-left:3px solid var(--tc);background:color-mix(in srgb,var(--tc) 20%,transparent);color:var(--ink)}
.ndetail-title{font-size:clamp(26px,4vw,48px);font-weight:900;letter-spacing:-.03em;margin:14px 0 8px;word-break:keep-all}
.ndetail-date{font-size:13px;color:var(--ink-2);margin-bottom:28px;font-family:'JetBrains Mono',monospace}
.ndetail-body{border-top:1px solid var(--line);padding-top:26px}
.ndetail-body p{font-size:clamp(15px,1.4vw,17px);color:#c3cee6;line-height:1.85;margin:0 0 18px;word-break:keep-all}
.ndetail-nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:36px;border-top:1px solid var(--line);padding-top:26px}
@media(max-width:640px){.nrow{flex-wrap:wrap;gap:8px}.ntitle{flex:1 1 100%;order:3}}
"""
# (CRUD 공용 모달/액션 버튼 CSS는 PAGE_CSS로 승격됨 — 클립·일정 페이지와 공유)

NOTICE_COLORS = {"공지": "#2f63ff", "이벤트": "#ff3d92", "업데이트": "#0fb5b0", "점검": "#ffcb45"}




def notice_form_modal():
    """공지 작성/수정 공용 모달 (목록·상세 페이지 공통 삽입)."""
    return """<div class="n-modal-bg" id="nModalBg" hidden role="dialog" aria-modal="true" aria-labelledby="nModalTitle">
  <div class="n-modal">
    <button class="n-modal-close" id="nModalClose" type="button" aria-label="닫기">×</button>
    <h2 id="nModalTitle">공지 작성</h2>
    <form id="nForm" novalidate>
      <label class="field"><span>카테고리</span>
        <select name="cat">
          <option value="공지">공지</option>
          <option value="이벤트">이벤트</option>
          <option value="업데이트">업데이트</option>
          <option value="점검">점검</option>
        </select></label>
      <label class="field"><span>제목</span><input type="text" name="title" maxlength="120" required></label>
      <label class="field"><span>날짜</span><input type="date" name="date" required></label>
      <label class="field"><span>본문 (줄바꿈으로 문단 구분)</span><textarea name="body" rows="6" required></textarea></label>
      <label class="n-pin-field" id="nPinField" style="display:none">
        <input type="checkbox" name="pinned"><span>상단 고정 (관리자만 지정 가능)</span></label>
      <p class="n-modal-msg" id="nModalMsg" role="status" aria-live="polite"></p>
      <button class="btn primary" type="submit">저장</button>
    </form>
  </div>
</div>"""


# 목록/상세 양쪽에서 공유하는 CRUD 헬퍼 JS (esc/색상/정렬/작성폼 로직).
# window.WhaleUI · window.WhaleData(assets/site.js)를 그대로 사용, Firebase URL은 재하드코딩하지 않는다.
_NOTICE_JS_SHARED = """
  var U=window.WhaleUI, D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var TC={"공지":"#2f63ff","이벤트":"#ff3d92","업데이트":"#0fb5b0","점검":"#ffcb45"};
  function tcOf(cat){return TC[cat]||'#2f63ff';}
  function sortNotices(arr){
    return arr.slice().sort(function(a,b){
      if(!!a.pinned!==!!b.pinned)return a.pinned?-1:1;
      return a.date<b.date?1:(a.date>b.date?-1:0);
    });
  }
  var nModalBg=document.getElementById('nModalBg'), nModalTitle=document.getElementById('nModalTitle'),
      nForm=document.getElementById('nForm'), nPinField=document.getElementById('nPinField'),
      nModalMsg=document.getElementById('nModalMsg');
  var formMode='create', formItem=null, onSaved=function(){};
  function openForm(mode,item,cb){
    formMode=mode;formItem=item;onSaved=cb||function(){};
    nModalMsg.textContent='';nForm.reset();
    nModalTitle.textContent=mode==='edit'?'공지 수정':'공지 작성';
    if(nPinField)nPinField.style.display=U.isAdmin()?'flex':'none';
    if(mode==='edit'&&item){
      nForm.cat.value=item.cat;nForm.title.value=item.title;nForm.date.value=item.date;
      nForm.body.value=(item.body||[]).join('\\n');
      if(nForm.pinned)nForm.pinned.checked=!!item.pinned;
    } else {
      nForm.date.value=new Date().toISOString().slice(0,10);
      if(nForm.pinned)nForm.pinned.checked=false;
    }
    nModalBg.hidden=false;
  }
  function closeForm(){nModalBg.hidden=true;}
  var nModalCloseBtn=document.getElementById('nModalClose');
  if(nModalCloseBtn)nModalCloseBtn.addEventListener('click',closeForm);
  if(nModalBg)nModalBg.addEventListener('click',function(e){if(e.target===nModalBg)closeForm();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nModalBg&&!nModalBg.hidden)closeForm();});
  if(nForm)nForm.addEventListener('submit',function(e){
    e.preventDefault();
    var title=nForm.title.value.trim(), date=nForm.date.value, cat=nForm.cat.value;
    var body=nForm.body.value.split('\\n').map(function(s){return s.trim();}).filter(Boolean);
    if(!title||!date||!body.length){nModalMsg.textContent='제목·날짜·본문을 모두 입력하세요.';return;}
    var payload={cat:cat,title:title,date:date,body:body};
    if(U.isAdmin())payload.pinned=!!(nForm.pinned&&nForm.pinned.checked);
    nModalMsg.textContent='저장 중...';
    var p=(formMode==='edit'&&formItem)?D.update('notices',formItem.id,payload):D.create('notices',payload);
    p.then(function(){closeForm();onSaved();}).catch(function(err){nModalMsg.textContent='저장 실패: '+(err&&err.message||err);});
  });
"""


def build_notices():
    body = (page_head_block("NOTICE", "공지사항", "공지사항")
            + '<div class="pg-tools img-ani bottom-top" id="nChips"></div>'
            + '<div class="n-actions img-ani bottom-top" id="nActions"></div>'
            + '<div class="nlist img-ani bottom-top" id="nList">불러오는 중...</div>'
            + notice_form_modal())
    js = "<script>(function(){" + _NOTICE_JS_SHARED + """
  var list=document.getElementById('nList'), chipsWrap=document.getElementById('nChips'),
      actionsEl=document.getElementById('nActions');
  var ALL=[], activeFilter='all';

  function renderActions(){
    var html='';
    if(U.isLoggedIn())html+='<button type="button" class="btn sm primary" id="nWriteBtn">+ 공지 작성</button>';
    actionsEl.innerHTML=html;
    var wb=document.getElementById('nWriteBtn');if(wb)wb.addEventListener('click',function(){openForm('create',null,reload);});
  }
  function renderChips(){
    var cats=[];ALL.forEach(function(n){if(cats.indexOf(n.cat)<0)cats.push(n.cat);});
    var html='<button type="button" class="chip'+(activeFilter==='all'?' active':'')+'" data-f="all">전체</button>'
      +cats.map(function(c){return '<button type="button" class="chip'+(activeFilter===c?' active':'')+'" data-f="'+esc(c)+'">'+esc(c)+'</button>';}).join('')
      +'<span class="pg-count" id="nCount"></span>';
    chipsWrap.innerHTML=html;
    [].slice.call(chipsWrap.querySelectorAll('.chip')).forEach(function(c){
      c.addEventListener('click',function(){activeFilter=c.getAttribute('data-f');renderChips();renderRows();});
    });
  }
  function rowActionsHtml(n){
    var h='';
    if(U.isAdmin())h+='<button type="button" class="n-btn'+(n.pinned?' pin-on':'')+'" data-act="pin" data-id="'+esc(n.id)+'">'+(n.pinned?'📌 해제':'📌 지정')+'</button>';
    if(U.canEdit(n)){
      h+='<button type="button" class="n-btn" data-act="edit" data-id="'+esc(n.id)+'">✏️ 수정</button>';
      h+='<button type="button" class="n-btn del" data-act="del" data-id="'+esc(n.id)+'">🗑 삭제</button>';
    }
    return h?'<span class="n-row-actions">'+h+'</span>':'';
  }
  function renderRows(){
    var filtered=activeFilter==='all'?ALL:ALL.filter(function(n){return n.cat===activeFilter;});
    var sorted=sortNotices(filtered);
    if(!sorted.length){
      list.innerHTML='<div class="nlist-msg">'+(ALL.length?'해당 분류의 공지가 없습니다.':'등록된 공지가 없습니다.')+'</div>';
    } else {
      list.innerHTML=sorted.map(function(n){
        return '<div class="nrow" data-cat="'+esc(n.cat)+'" data-id="'+esc(n.id)+'" role="button" tabindex="0">'
          +(n.pinned?'<span class="npin" title="상단 고정">📌</span>':'')
          +'<span class="ncat" style="--tc:'+tcOf(n.cat)+'">'+esc(n.cat)+'</span>'
          +'<span class="ntitle">'+esc(n.title)+'</span>'
          +'<span class="ndate">'+esc(n.date)+'</span>'
          +rowActionsHtml(n)
          +'<span class="narrow" aria-hidden="true">→</span></div>';
      }).join('');
    }
    var count=document.getElementById('nCount');
    if(count)count.textContent=(activeFilter==='all'?'전체':activeFilter)+' '+sorted.length+'건';
  }
  function reload(){
    return D.list('notices').then(function(items){
      ALL=items;renderActions();renderChips();renderRows();
    }).catch(function(err){
      list.innerHTML='<div class="nlist-msg">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
    });
  }
  list.addEventListener('click',function(e){
    var btn=e.target.closest&&e.target.closest('[data-act]');
    if(btn){
      e.stopPropagation();
      var id=btn.getAttribute('data-id'),act=btn.getAttribute('data-act');
      var item=ALL.filter(function(x){return x.id===id;})[0];
      if(!item)return;
      if(act==='pin')togglePin(item);
      else if(act==='edit')openForm('edit',item,reload);
      else if(act==='del')removeNotice(item);
      return;
    }
    var row=e.target.closest&&e.target.closest('.nrow');
    if(row)location.href='notice.html?id='+encodeURIComponent(row.getAttribute('data-id'));
  });
  list.addEventListener('keydown',function(e){
    if(e.key!=='Enter'&&e.key!==' ')return;
    var row=e.target.closest&&e.target.closest('.nrow');
    if(row&&e.target===row){e.preventDefault();location.href='notice.html?id='+encodeURIComponent(row.getAttribute('data-id'));}
  });
  function togglePin(item){
    D.update('notices',item.id,{pinned:!item.pinned}).then(reload).catch(function(err){alert('처리 실패: '+(err&&err.message||err));});
  }
  function removeNotice(item){
    if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
    D.remove('notices',item.id).then(reload).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
  }
  document.addEventListener('whale:authchange',reload);  // 로그인/로그아웃 시 버튼 재렌더
  reload();
})();</script>"""
    write("notices", "공지사항", body, NOTICE_CSS, scripts=js)


def build_notice():
    body = (page_head_block("NOTICE", "공지사항", "공지 상세")
            + '<article class="img-ani bottom-top" id="nDetail"></article>'
            + notice_form_modal())
    js = "<script>(function(){" + _NOTICE_JS_SHARED + """
  var detail=document.getElementById('nDetail');
  var qs=new URLSearchParams(location.search), id=qs.get('id'), legacyIdx=qs.get('i');
  var N=[], idx=0;
  function load(){
    return D.list('notices').then(function(items){
      N=sortNotices(items);
      if(id){
        idx=N.findIndex(function(n){return n.id===id;});
        if(idx<0)idx=0;
      } else if(legacyIdx!=null&&!isNaN(parseInt(legacyIdx,10))){
        idx=Math.min(Math.max(parseInt(legacyIdx,10),0),Math.max(N.length-1,0));
      } else idx=0;
      render();
    }).catch(function(err){
      detail.innerHTML='<div class="nlist-msg">불러오기 실패: '+esc(err&&err.message||err)+'</div>';
    });
  }
  function render(){
    var n=N[idx];
    if(!n){
      detail.innerHTML='<div class="nlist-msg">등록된 공지가 없습니다.<br><a class="btn sm" href="notices.html">목록으로</a></div>';
      return;
    }
    id=n.id;
    document.title=n.title+' · 고래상사';
    if(history.replaceState)history.replaceState(null,'','notice.html?id='+encodeURIComponent(n.id));
    var paras=(n.body||[]).map(function(p){return '<p>'+esc(p)+'</p>';}).join('');
    var manage='';
    if(U.isAdmin())manage+='<button class="btn sm" id="nDetPin" type="button">'+(n.pinned?'📌 고정 해제':'📌 상단 고정')+'</button>';
    if(U.canEdit(n)){
      manage+='<button class="btn sm" id="nDetEdit" type="button">✏️ 수정</button>';
      manage+='<button class="btn sm" id="nDetDel" type="button">🗑 삭제</button>';
    }
    detail.innerHTML=
      '<span class="ndetail-cat" style="--tc:'+tcOf(n.cat)+'">'+esc(n.cat)+'</span>'
      +'<h2 class="ndetail-title">'+(n.pinned?'📌 ':'')+esc(n.title)+'</h2>'
      +'<div class="ndetail-date">'+esc(n.date)+(n.ownerNick?' · '+esc(n.ownerNick):'')+'</div>'
      +'<div class="ndetail-body">'+paras+'</div>'
      +'<div class="ndetail-nav"><button class="btn sm" id="nPrev" type="button">← 이전 글</button>'
      +'<button class="btn sm" id="nNext" type="button">다음 글 →</button>'
      +manage
      +'<a class="btn sm primary" href="notices.html">목록으로</a></div>';
    document.getElementById('nPrev').onclick=function(){idx=(idx-1+N.length)%N.length;render();};
    document.getElementById('nNext').onclick=function(){idx=(idx+1)%N.length;render();};
    var pinBtn=document.getElementById('nDetPin');
    if(pinBtn)pinBtn.onclick=function(){
      D.update('notices',n.id,{pinned:!n.pinned}).then(load).catch(function(err){alert('처리 실패: '+(err&&err.message||err));});
    };
    var editBtn=document.getElementById('nDetEdit');
    if(editBtn)editBtn.onclick=function(){openForm('edit',n,load);};
    var delBtn=document.getElementById('nDetDel');
    if(delBtn)delBtn.onclick=function(){
      if(!confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.'))return;
      D.remove('notices',n.id).then(function(){location.href='notices.html';}).catch(function(err){alert('삭제 실패: '+(err&&err.message||err));});
    };
  }
  document.addEventListener('whale:authchange',load);  // 로그인/로그아웃 시 관리 버튼 재렌더
  load();
})();</script>"""
    write("notice", "공지 상세", body, NOTICE_CSS, scripts=js)


# ---------- 아키타입: 멀티뷰 (라이브 그리드) ----------

MULTIVIEW_CSS = PAGE_CSS + """
/* 멀티뷰는 전체 화면 폭 사용 (헤더/바/재생/목록 모두 동일 폭) */
.pg-wrap{max-width:none;padding-left:clamp(20px,3vw,56px);padding-right:clamp(20px,3vw,56px)}
.mv-bar{position:sticky;top:64px;z-index:30;display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  background:rgba(7,10,20,.92);backdrop-filter:blur(12px);border:1px solid var(--line-2);border-radius:14px;
  padding:12px 16px;margin-bottom:clamp(22px,3vw,32px)}
.mv-bar .cnt{font-weight:800;font-size:14px;flex:0 0 auto}
.mv-bar .cnt b{color:var(--accent)}
.mv-search{display:flex;gap:8px;margin-left:auto;flex:1 1 260px;max-width:420px}
.mv-search input{flex:1;font:inherit;font-size:14px;padding:9px 12px;border:1px solid var(--line-2);border-radius:10px;
  background:rgba(255,255,255,.04);color:var(--ink)}
.mv-search input:focus{outline:none;border-color:var(--brand);background:rgba(255,255,255,.07)}
.mv-layout{display:flex;gap:clamp(16px,2vw,24px);align-items:flex-start;margin-bottom:clamp(24px,3vw,36px)}
.mv-stage{flex:1 1 auto;min-width:0;display:grid;gap:10px;position:sticky;top:130px}
.mv-stage.grid-1{grid-template-columns:1fr}
.mv-stage.grid-2{grid-template-columns:1fr 1fr}
.mv-stage.grid-4{grid-template-columns:1fr 1fr}
.mv-stage.is-empty{grid-template-columns:1fr;place-items:center;min-height:min(58vh,520px);
  border:2px dashed var(--line-2);border-radius:16px;background:rgba(255,255,255,.015)}
.mv-stage-ph{text-align:center;color:var(--ink-2);font-size:14px;line-height:1.65;padding:24px}
.mv-stage-ph .big{font-size:clamp(40px,6vw,68px);opacity:.55;margin-bottom:14px}
/* 전체화면: 스테이지를 모니터 가득, 영상은 비율 무시하고 칸을 꽉 채움 */
.mv-stage:fullscreen,.mv-stage:-webkit-full-screen{width:100%;height:100%;gap:6px;padding:6px;
  background:#000;grid-auto-rows:1fr;place-content:stretch}
.mv-stage:fullscreen .video-wrapper,.mv-stage:-webkit-full-screen .video-wrapper{aspect-ratio:auto;height:100%;border-radius:6px}
.video-wrapper{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#000;border:1px solid var(--line-2)}
.video-wrapper iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.video-wrapper .close-btn{position:absolute;top:8px;right:8px;z-index:5;width:30px;height:30px;border-radius:8px;
  border:none;background:rgba(0,0,0,.65);color:#fff;font-size:14px;font-weight:800;cursor:pointer}
.video-wrapper .close-btn:hover{background:var(--hot)}
@media(max-width:640px){.mv-stage.grid-2,.mv-stage.grid-4{grid-template-columns:1fr}}
.mv-side{flex:0 0 clamp(230px,18vw,280px);position:sticky;top:130px;
  max-height:calc(100vh - 150px);display:flex;flex-direction:column;
  border:1px solid var(--line-2);border-radius:16px;background:rgba(7,10,20,.55);overflow:hidden}
.mv-sec-h{font-size:15px;font-weight:900;letter-spacing:-.02em;margin:0;display:flex;align-items:center;gap:9px;
  padding:14px 16px;border-bottom:1px solid var(--line-2);background:rgba(7,10,20,.6)}
.mv-sec-h .live-dot{width:9px;height:9px;border-radius:50%;background:var(--hot);animation:pulse 1.8s infinite}
.mv-grid{display:flex;flex-direction:column;gap:8px;padding:12px;overflow-y:auto}
.mv-side .mv-card{display:flex;align-items:stretch;flex:0 0 auto}
.mv-side .mv-thumb{flex:0 0 104px;aspect-ratio:16/9}
.mv-side .mv-info{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center}
.mv-side .mv-thumb .ava{width:40px;height:40px;font-size:16px}
.mv-side .mv-view{font-size:10px;padding:2px 6px;bottom:6px;right:6px}
.mv-side .mv-badge{font-size:9px;padding:3px 6px;top:6px;left:6px}
@media(max-width:900px){
  .mv-layout{flex-direction:column}
  .mv-stage{position:static;width:100%}
  .mv-side{flex:none;width:100%;position:static;max-height:none}
  .mv-grid{flex-direction:row;flex-wrap:wrap;overflow:visible}
  .mv-side .mv-card{flex:1 1 260px}
}
.mv-card{position:relative;border-radius:14px;overflow:hidden;border:1px solid var(--line);cursor:pointer;
  transition:border-color .2s,transform .2s,box-shadow .2s}
.mv-card:hover{transform:translateY(-3px);border-color:var(--brand);box-shadow:0 12px 40px rgba(47,99,255,.28)}
.mv-card.sel{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent)}
.mv-thumb{position:relative;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;background:#0f1730}
.mv-thumb>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.mv-thumb .ava{width:60px;height:60px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:900;color:#fff;border:2px solid rgba(255,255,255,.5);z-index:1}
.mv-thumb .ava img{width:100%;height:100%;object-fit:cover}
.mv-badge{position:absolute;top:10px;left:10px;z-index:2;display:flex;align-items:center;gap:6px;
  font-size:11px;font-weight:800;letter-spacing:.05em;padding:4px 9px;border-radius:6px;background:var(--hot);color:#fff}
.mv-badge .d{width:6px;height:6px;border-radius:50%;background:#fff;animation:pulse 1.8s infinite}
.mv-view{position:absolute;bottom:10px;right:10px;z-index:2;font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;
  background:rgba(0,0,0,.62);color:#fff}
.mv-chk{position:absolute;top:8px;right:10px;z-index:2;font-size:18px;color:var(--accent);opacity:0;transition:.15s}
.mv-card.sel .mv-chk{opacity:1}
.mv-info{padding:11px 13px;background:var(--surface)}
.mv-info .nm{font-size:14px;font-weight:800}
.mv-info .tt{font-size:11.5px;color:var(--ink-2);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mv-empty{text-align:center;padding:clamp(40px,8vw,90px) 0;color:var(--ink-2)}
.mv-empty .big{font-size:clamp(36px,6vw,64px);opacity:.5;margin-bottom:14px}
@media(prefers-reduced-motion:reduce){.mv-badge .d,.mv-sec-h .live-dot{animation:none}}
"""


def build_multiview():
    # 멤버 메타(id -> 이름/색/이니셜/이미지) 주입 — 라이브 데이터의 폴백 표시용
    meta = {m["soop"]: {"name": m["name"], "color": m["color"], "initials": m["initials"],
                        "img": ("../" + m["img"]) if m.get("img") else ""}
            for m in MEMBERS if m.get("soop")}
    inject = ('<script>window.WHALE_META=' + json.dumps(meta, ensure_ascii=False) + ';'
              'window.STATUS_URL="https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/status.json";'
              'window.SEARCH_URL="https://whale-status-worker.kyefyx.workers.dev/search/bj";</script>')
    body = (page_head_block("MULTIVIEW", "동시 시청", "멀티뷰 시청")
            + '<div class="mv-bar img-ani bottom-top">'
              '<span class="cnt">선택 <b id="mvCnt">0</b> / 4</span>'
              '<button class="btn sm" id="mvFullBtn" type="button" title="재생 영역 전체화면">⛶ 전체화면</button>'
              '<form class="mv-search" id="mvSearchForm" autocomplete="off">'
              '<input type="text" id="mvSearch" placeholder="외부 스트리머 닉네임 검색 (숲)">'
              '<button class="btn sm primary" type="submit">검색</button></form></div>'
            + '<div class="mv-layout img-ani bottom-top">'
              '<div class="mv-stage is-empty" id="mvStage"></div>'
              '<aside class="mv-side">'
              '<h3 class="mv-sec-h"><span class="live-dot"></span>지금 방송 중'
              '<span style="font-size:12px;font-weight:600;color:var(--ink-2)" id="mvLiveInfo"></span></h3>'
              '<div class="mv-grid" id="mvGrid"></div></aside></div>')
    js = r"""<script>(function(){
  var META=window.WHALE_META||{},SU=window.STATUS_URL,SEARCH=window.SEARCH_URL;
  var grid=document.getElementById('mvGrid'),stage=document.getElementById('mvStage');
  var cntEl=document.getElementById('mvCnt'),info=document.getElementById('mvLiveInfo');
  var sel=[],ext={},lastLive=[];
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function stageCls(n){return 'mv-stage '+(n===1?'grid-1':n===2?'grid-2':'grid-4');}
  function renderStage(){
    if(sel.length===0){
      stage.className='mv-stage is-empty';
      stage.innerHTML='<div class="mv-stage-ph"><div class="big">🐳</div>'
        +'오른쪽 목록에서 방송을 선택하면<br>여기에서 최대 <b>4개</b>까지 동시에 볼 수 있어요.</div>';
    }else{
      stage.className=stageCls(sel.length);
      var ph=stage.querySelector('.mv-stage-ph');if(ph)ph.remove();
      var have={};[].forEach.call(stage.querySelectorAll('.video-wrapper'),function(w){
        var id=w.getAttribute('data-id');if(sel.indexOf(id)<0)w.remove();else have[id]=1;});
      sel.forEach(function(id){
        if(have[id])return;
        var w=document.createElement('div');w.className='video-wrapper';w.setAttribute('data-id',id);
        w.innerHTML='<button class="close-btn" aria-label="닫기">×</button>'
          +'<iframe src="https://play.sooplive.com/'+encodeURIComponent(id)+'/embed" '
          +'allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen scrolling="no"></iframe>';
        w.querySelector('.close-btn').addEventListener('click',function(){toggle(id);});
        stage.appendChild(w);
      });
    }
    cntEl.textContent=sel.length;
    [].forEach.call(grid.querySelectorAll('.mv-card'),function(c){
      c.classList.toggle('sel',sel.indexOf(c.getAttribute('data-id'))>=0);});
  }
  function toggle(id){
    var k=sel.indexOf(id);
    if(k>=0)sel.splice(k,1);
    else{if(sel.length>=4){alert('최대 4명까지 동시 시청할 수 있습니다.');return;}sel.push(id);}
    renderStage();
  }
  function card(m){
    var thumb=m.thumbnail?'<img src="'+esc(m.thumbnail)+'" alt="'+esc(m.name)+'" onerror="this.style.display=\'none\'">':'';
    var ava='<div class="ava" style="background:'+(m.color||'#1f2a52')+'">'
      +(m.img?'<img src="'+esc(m.img)+'" onerror="this.style.display=\'none\'">':esc(m.initials||''))+'</div>';
    return '<div class="mv-card" data-id="'+esc(m.id)+'" role="button" tabindex="0">'
      +'<div class="mv-thumb">'+thumb+ava
      +'<span class="mv-badge"><span class="d"></span>LIVE</span>'
      +'<span class="mv-view">👁 '+(m.viewers||0).toLocaleString()+'</span>'
      +'<span class="mv-chk">✔</span></div>'
      +'<div class="mv-info"><div class="nm">'+esc(m.name)+'</div><div class="tt">'+esc(m.title||'방송 중')+'</div></div></div>';
  }
  function renderGrid(live){
    if(!live.length){grid.innerHTML='<div class="mv-empty" style="grid-column:1/-1"><div class="big">🌙</div>'
      +'현재 방송 중인 멤버가 없습니다.<br>방송이 시작되면 자동으로 표시됩니다.</div>';info.textContent='';return;}
    info.textContent='· '+live.length+'명';
    grid.innerHTML=live.map(card).join('');
    [].forEach.call(grid.querySelectorAll('.mv-card'),function(c){
      var id=c.getAttribute('data-id');
      c.addEventListener('click',function(){toggle(id);});
      c.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle(id);}});
    });
    renderStage();
  }
  function load(){
    fetch(SU+'?v='+Date.now()).then(function(r){return r.json();}).then(function(d){
      var live=[];
      if(d&&d.members)Object.keys(d.members).forEach(function(k){
        var m=d.members[k];if(!m.is_live)return;
        var meta=META[m.id]||{};
        live.push({id:m.id,name:m.name||meta.name||m.id,title:m.title,viewers:m.viewers,
          thumbnail:m.thumbnail,color:meta.color,initials:meta.initials,img:meta.img});
      });
      live.sort(function(a,b){return (b.viewers||0)-(a.viewers||0);});
      lastLive=live;renderGrid(live);
    }).catch(function(){grid.innerHTML='<div class="mv-empty" style="grid-column:1/-1">라이브 정보를 불러오지 못했습니다.</div>';});
  }
  // 외부 스트리머 검색 → 선택
  document.getElementById('mvSearchForm').addEventListener('submit',function(e){
    e.preventDefault();
    var q=document.getElementById('mvSearch').value.trim();if(!q)return;
    fetch(SEARCH+'?q='+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(list){
      var arr=Array.isArray(list)?list:(list&&list.results)||[];
      if(!arr.length){alert('검색 결과가 없습니다.');return;}
      var s=arr[0],id=s.id||s.bj_id||s.user_id;if(!id){alert('결과를 해석할 수 없습니다.');return;}
      if(sel.indexOf(id)<0){if(sel.length>=4){alert('최대 4명까지 시청할 수 있습니다.');return;}sel.push(id);renderStage();}
    }).catch(function(){alert('검색에 실패했습니다. (워커 응답 없음)');});
  });
  // 재생 영역 전체화면
  var fullBtn=document.getElementById('mvFullBtn');
  function fsEl(){return document.fullscreenElement||document.webkitFullscreenElement;}
  fullBtn.addEventListener('click',function(){
    if(fsEl()){(document.exitFullscreen||document.webkitExitFullscreen).call(document);return;}
    if(!sel.length){alert('먼저 볼 방송을 선택하세요.');return;}
    var req=stage.requestFullscreen||stage.webkitRequestFullscreen;
    if(req)req.call(stage);else alert('이 브라우저는 전체화면을 지원하지 않습니다.');
  });
  function syncFs(){fullBtn.textContent=(fsEl()===stage)?'⛶ 전체화면 종료':'⛶ 전체화면';}
  document.addEventListener('fullscreenchange',syncFs);
  document.addEventListener('webkitfullscreenchange',syncFs);

  load();setInterval(load,300000);
})();</script>"""
    write("multiview", "멀티뷰 시청", body, MULTIVIEW_CSS, scripts=inject + js)


# ---------- 아키타입: 관리자 (게이팅 정적 목업) ----------

ADMIN_CSS = PAGE_CSS + """
.adm-gate{text-align:center;padding:clamp(48px,10vw,120px) 0}
.adm-gate .lock{font-size:clamp(44px,7vw,80px);margin-bottom:18px;opacity:.6}
.adm-gate h2{font-size:clamp(22px,3vw,32px);font-weight:900;margin:0 0 10px}
.adm-gate p{color:var(--ink-2);margin:0 0 24px;line-height:1.7}
.adm-body[hidden]{display:none}
.adm-note{font-size:12.5px;color:var(--warn);background:color-mix(in srgb,var(--warn) 12%,transparent);
  border:1px solid color-mix(in srgb,var(--warn) 30%,transparent);border-radius:10px;padding:12px 16px;margin-bottom:26px}
.adm-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-bottom:clamp(32px,4vw,48px)}
.adm-stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 18px}
.adm-stat .n{font-size:clamp(28px,3.4vw,42px);font-weight:900;letter-spacing:-.02em;color:var(--brand)}
.adm-stat .u{font-size:13px;color:var(--ink-2);margin-top:4px}
.adm-quick{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.adm-quick a{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 20px;
  display:flex;flex-direction:column;gap:6px;transition:border-color .2s,transform .2s}
.adm-quick a:hover{border-color:var(--brand);transform:translateY(-3px)}
.adm-quick .ic{font-size:26px}
.adm-quick .t{font-weight:800;font-size:16px}
.adm-quick .d{font-size:12.5px;color:var(--ink-2)}
.adm-toolbar{display:flex;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap}
.adm-toolbar h3{margin:0;font-size:20px;font-weight:900}
.adm-toolbar .btn{margin-left:auto}
.adm-table{width:100%;border-collapse:collapse;font-size:14px}
.adm-table th,.adm-table td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line)}
.adm-table th{font-size:12px;font-weight:800;color:var(--ink-2);text-transform:uppercase;letter-spacing:.06em}
.adm-table tr:hover td{background:rgba(255,255,255,.02)}
.adm-table .act{display:flex;gap:6px}
.adm-table .mini{font-size:12px;font-weight:700;padding:5px 10px;border-radius:8px;border:1px solid var(--line-2);
  background:var(--surface-2);color:var(--ink);cursor:pointer}
.adm-table .mini.del:hover{border-color:var(--hot);color:var(--hot)}
.adm-table .mini:hover{border-color:var(--brand)}
.adm-wrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:14px}
"""

ADMIN_GATE_JS = """<script>(function(){
  function isAdmin(){try{var u=JSON.parse(sessionStorage.getItem('soop_user')||'null');
    return !!(u&&(u.role==='admin'||u.role==='editor'));}catch(e){return false;}}
  var gate=document.getElementById('admGate'),bodyEl=document.getElementById('admBody');
  function sync(){var a=isAdmin();if(gate)gate.hidden=a;if(bodyEl)bodyEl.hidden=!a;}
  sync();document.addEventListener('whale:authchange',sync);
  var lb=document.getElementById('admLogin');
  if(lb)lb.addEventListener('click',function(){var b=document.getElementById('loginBtn');if(b)b.click();});
  [].forEach.call(document.querySelectorAll('[data-demo]'),function(el){
    el.addEventListener('click',function(){alert('이 관리 테이블은 미리보기입니다. 실제 등록·수정·삭제는 클립/공지/일정/아카이브 각 페이지에서 로그인 후 바로 가능합니다.');});
  });
})();</script>"""


def admin_gate(inner):
    return ('<div class="adm-gate" id="admGate" hidden><div class="lock">🔒</div>'
            '<h2>관리자 전용 페이지</h2>'
            '<p>이 페이지는 숲(SOOP) 관리자 권한이 필요합니다.<br>상단 로그인 버튼으로 인증해 주세요.</p>'
            '<button class="btn primary" id="admLogin">관리자 로그인</button></div>'
            f'<div class="adm-body" id="admBody" hidden>{inner}</div>')


def build_admin_dashboard():
    # 07-11 critique 반영: "데모 환경" 거짓 문구 제거(CRUD는 Phase A/B로 이미 라이브),
    # 통계 카드는 D.list 실데이터 카운트로 채움(멤버 16인만 빌드타임 정적).
    inner = (
        '<div class="adm-note">공지·클립·일정·아카이브는 각 페이지에서 직접 작성/수정합니다. 저장은 즉시 반영됩니다.</div>'
        '<div class="adm-stats">'
        f'<div class="adm-stat"><div class="n">{len(MEMBERS)}</div><div class="u">멤버</div></div>'
        '<div class="adm-stat"><div class="n" data-cnt="clips">—</div><div class="u">클립</div></div>'
        '<div class="adm-stat"><div class="n" data-cnt="contests">—</div><div class="u">아카이브</div></div>'
        '<div class="adm-stat"><div class="n" data-cnt="schedules">—</div><div class="u">일정</div></div>'
        '<div class="adm-stat"><div class="n" data-cnt="notices">—</div><div class="u">공지</div></div>'
        '</div>'
        '<div class="adm-quick">'
        '<a href="admin-clips.html"><span class="ic">🎬</span><span class="t">클립 관리</span><span class="d">베스트 클립 등록·수정·삭제</span></a>'
        '<a href="admin-notices.html"><span class="ic">📢</span><span class="t">공지/일정 관리</span><span class="d">공지사항·방송 일정 관리</span></a>'
        '<a href="admin-members.html"><span class="ic">👥</span><span class="t">멤버/크루 관리</span><span class="d">멤버 정보·직급 관리</span></a>'
        '</div>')
    stats_js = """<script>(function(){
  var D=window.WhaleData;if(!D)return;
  ['clips','contests','schedules','notices'].forEach(function(col){
    D.list(col).then(function(items){
      var el=document.querySelector('[data-cnt="'+col+'"]');if(el)el.textContent=items.length;
    }).catch(function(){});
  });
})();</script>"""
    body = page_head_block("ADMIN", "관리자 전용", "관리자 홈") + admin_gate(inner)
    write("admin", "관리자 홈", body, ADMIN_CSS, scripts=ADMIN_GATE_JS + stats_js)


def build_admin_login():
    inner = (
        '<div class="adm-note">관리자 권한은 숲(SOOP) 계정으로 확인됩니다. 아래 버튼 또는 상단 로그인으로 인증하세요.</div>'
        '<div style="max-width:420px"><button class="btn primary" id="admLogin2" style="width:100%;justify-content:center;padding:14px">🔵 숲(SOOP) 계정으로 로그인</button>'
        '<p style="color:var(--ink-2);font-size:13px;margin-top:16px;line-height:1.7">권한 계정만 접근할 수 있습니다. '
        '관리자(admin)는 전체 관리, 편집자(editor)는 일정·공지 관리가 가능합니다.</p></div>')
    # 로그인 페이지는 게이트 없이 항상 로그인 유도
    body = page_head_block("ADMIN", "관리자 전용", "로그인") + inner
    extra = '<script>var b2=document.getElementById("admLogin2");if(b2)b2.addEventListener("click",function(){var b=document.getElementById("loginBtn");if(b)b.click();});</script>'
    write("admin-login", "관리자 로그인", body, ADMIN_CSS, scripts=extra)


def admin_table(title, columns, rows_html, add_label):
    return (f'<div class="adm-toolbar"><h3>{esc(title)}</h3>'
            f'<button class="btn primary sm" data-demo>+ {esc(add_label)}</button></div>'
            '<div class="adm-wrap"><table class="adm-table"><thead><tr>'
            + "".join(f'<th>{esc(c)}</th>' for c in columns) + '<th>관리</th></tr></thead>'
            f'<tbody>{rows_html}</tbody></table></div>')


def _act_cell():
    return ('<td><div class="act"><button class="mini" data-demo>수정</button>'
            '<button class="mini del" data-demo>삭제</button></div></td>')


def build_admin_clips():
    rows = "".join(
        f'<tr><td>{i+1}</td><td>{esc(c["title"])}</td><td>{esc(c["creator"])}</td>'
        f'<td>{esc(c["category"])}</td><td>{esc(c.get("date",""))}</td>{_act_cell()}</tr>'
        for i, c in enumerate(CLIPS))
    inner = admin_table("클립 관리", ["#", "제목", "제작자", "카테고리", "날짜"], rows, "새 클립 등록")
    body = page_head_block("ADMIN", "관리자 전용", "클립 관리") + admin_gate(inner)
    write("admin-clips", "클립 관리", body, ADMIN_CSS, scripts=ADMIN_GATE_JS)


def build_admin_notices():
    rows = "".join(
        f'<tr><td>{"📌" if n.get("pinned") else ""}</td><td>{esc(n["title"])}</td>'
        f'<td>{esc(n["cat"])}</td><td>{esc(n["date"])}</td>{_act_cell()}</tr>'
        for n in NOTICES)
    nt = admin_table("공지사항 관리", ["고정", "제목", "분류", "날짜"], rows, "새 공지 작성")
    srows = "".join(
        f'<tr><td>{esc(e["date"])}</td><td>{esc(e["time"])}</td><td>{esc(e["title"])}</td>'
        f'<td>{esc(e["type"])}</td>{_act_cell()}</tr>'
        for e in SCHEDULE)
    st = admin_table("방송 일정 관리", ["날짜", "시간", "제목", "유형"], srows, "새 일정 추가")
    inner = nt + '<div style="height:36px"></div>' + st
    body = page_head_block("ADMIN", "관리자 전용", "공지/일정 관리") + admin_gate(inner)
    write("admin-notices", "공지/일정 관리", body, ADMIN_CSS, scripts=ADMIN_GATE_JS)


def build_admin_members():
    ordered = sorted(MEMBERS, key=lambda m: m["rank"])
    rows = "".join(
        f'<tr><td>{esc(m["name"])}</td><td>{esc(m["role"])}</td><td>{esc(m["dept"])}</td>'
        f'<td>{m["rank"]}</td>{_act_cell()}</tr>' for m in ordered)
    inner = admin_table("멤버/크루 관리", ["이름", "직책", "부서", "직급순"], rows, "새 멤버 등록")
    body = page_head_block("ADMIN", "관리자 전용", "멤버/크루 관리") + admin_gate(inner)
    write("admin-members", "멤버/크루 관리", body, ADMIN_CSS, scripts=ADMIN_GATE_JS)


# ---------- 아키타입: 통계 · 전적 (운영 ranking.html 리워크 재구현, §2.5-2) ----------

STATS_CSS = PAGE_CSS + """
.st-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:clamp(28px,4vw,44px)}
.st-tile{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px}
.st-tile .n{font-size:clamp(24px,3vw,34px);font-weight:900;letter-spacing:-.03em}
.st-tile .u{font-size:12.5px;color:var(--ink-2);margin-top:2px}
.st-tile .s{font-size:12px;color:var(--accent);margin-top:2px}
.st-cols{display:grid;grid-template-columns:1fr 1fr;gap:clamp(20px,3vw,36px)}
@media(max-width:860px){.st-cols{grid-template-columns:1fr}}
.st-panel h3{margin:0 0 6px;font-size:19px;font-weight:900;letter-spacing:-.02em}
.st-panel .st-cap{margin:0 0 16px;font-size:12.5px;color:var(--ink-2)}
.st-row{display:grid;grid-template-columns:minmax(72px,auto) 1fr auto;align-items:center;gap:12px;
  padding:10px 0;border-top:1px solid var(--line)}
.st-row:first-of-type{border-top:none}
.st-row .nm{font-size:14px;font-weight:700;word-break:keep-all}
.st-row .val{font-size:12.5px;color:var(--ink-2);white-space:nowrap;font-variant-numeric:tabular-nums}
.st-bar{height:8px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden;display:flex}
.st-bar .w{background:var(--accent)}
.st-bar .l{background:rgba(255,77,77,.55)}
.st-badge{font-size:11.5px;font-weight:800;padding:3px 9px;border-radius:999px;white-space:nowrap}
.st-badge.high{background:rgba(15,181,176,.16);color:var(--accent)}
.st-badge.mid{background:rgba(255,203,69,.14);color:var(--warn)}
.st-badge.low{background:rgba(255,77,77,.14);color:var(--hot)}
.st-gap{height:clamp(24px,3vw,36px)}
.st-empty{padding:44px 0;text-align:center;color:var(--ink-2);font-size:14px}
.st-foot{margin-top:clamp(28px,4vw,44px)}
@media(max-width:480px){.st-row{grid-template-columns:minmax(60px,auto) 1fr auto;gap:8px}
  .st-row .val{font-size:11px}.st-row .nm{font-size:13px}}
"""


def build_stats():
    """통계 · 전적 — /rework/contests(크루대전만)를 집계해 요약·멤버별·게임별·크루별 통계 렌더.
    운영 ranking.js 로직 이식 + 리워크 규약: games/opponents result true=승, 다자전은 rank 규칙."""
    member_names = json.dumps([m["name"] for m in MEMBERS], ensure_ascii=False)
    body = (page_head_block("STATS", "콘텐츠 아카이브", "통계 · 전적")
            + '<div class="st-tiles img-ani bottom-top" id="stTiles"></div>'
            + '<div class="st-cols img-ani bottom-top">'
              '<div class="st-panel"><h3>사원별 대회 성적</h3><p class="st-cap">참여율 순 · 승률은 참여 대회 기준</p><div id="stMembers"><div class="st-empty">불러오는 중...</div></div></div>'
              '<div class="st-panel"><h3>게임별 승패</h3><p class="st-cap">크루대전에서 치른 종목별 전적</p><div id="stGames"></div></div>'
              '</div>'
            + '<div class="st-gap"></div>'
            + '<div class="st-panel img-ani bottom-top"><h3>상대 크루 전적</h3><p class="st-cap">현재 크루명 기준 · 팀명에 마우스를 올리면 과거 이름 표시</p><div id="stCrews"></div></div>'
            + '<div class="st-foot img-ani bottom-top"><a class="btn sm" href="archive.html">전체 기록은 통합 아카이브에서 →</a></div>')

    js = """<script>(function(){
  var D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var MEMBER_NAMES=""" + member_names + """;
  var CREWS_URL='https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app/crews.json';
  var elT=document.getElementById('stTiles'),elM=document.getElementById('stMembers'),
      elG=document.getElementById('stGames'),elC=document.getElementById('stCrews');
  function badgeCls(p){return p>=60?'high':p>=40?'mid':'low';}
  function bar(w,l){var t=w+l;if(!t)return '';var wp=Math.round(w/t*100);
    return '<div class="st-bar"><span class="w" style="width:'+wp+'%"></span><span class="l" style="width:'+(100-wp)+'%"></span></div>';}
  /* 다자전: opponents는 상위 등수부터 — index >= rank-1 이면 고래상사가 위(승) */
  function oppResult(c,i){
    if((c.opponents||[]).length===1){var r=c.opponents[0].result;return r===undefined?null:!!r;}
    if(c.rank==null)return null;
    return i>=c.rank-1;
  }
  Promise.all([
    D.list('contests'),
    fetch(CREWS_URL+'?v='+Date.now()).then(function(r){return r.ok?r.json():{};}).catch(function(){return {};})
  ]).then(function(res){
    var all=res[0].filter(function(c){return (c.category||'크루대전')!=='컨텐츠';}),crews=res[1]||{};
    if(!all.length){
      elT.innerHTML='';elM.innerHTML='<div class="st-empty">아직 집계할 크루대전 기록이 없습니다.</div>';
      elG.innerHTML='';elC.innerHTML='<div class="st-empty">기록이 쌓이면 자동으로 채워집니다.</div>';return;
    }
    all.forEach(function(c){c._g=Object.keys(c.games||{}).map(function(k){return c.games[k]||{};});});
    var totalEvents=all.length,totalGames=0,totalWins=0,memberMap={},gameMap={},crewMap={};
    all.forEach(function(c){
      var w=c._g.filter(function(g){return g.result;}).length,l=c._g.length-w;
      totalGames+=c._g.length;totalWins+=w;
      var won=w>l;
      (c.members||[]).forEach(function(n){
        if(!memberMap[n])memberMap[n]={att:0,win:0};
        memberMap[n].att++;if(won)memberMap[n].win++;
      });
      c._g.forEach(function(g){
        if(!g.name)return;
        if(!gameMap[g.name])gameMap[g.name]={w:0,l:0};
        g.result?gameMap[g.name].w++:gameMap[g.name].l++;
      });
      (c.opponents||[]).forEach(function(op,i){
        var key=op.crewId||('name:'+(op.name||'?'));
        var crew=op.crewId?crews[op.crewId]:null;
        if(crew&&crew.currentName==='고래상사')return;
        if(!crewMap[key])crewMap[key]={w:0,l:0,name:(crew&&crew.currentName)||op.name||'?',
          past:crew&&Array.isArray(crew.aliases)?crew.aliases.filter(function(a){return a!==crew.currentName;}):[]};
        var r=oppResult(c,i);
        if(r===true)crewMap[key].w++;else if(r===false)crewMap[key].l++;
      });
    });
    var winRate=totalGames?Math.round(totalWins/totalGames*100):0;
    var top=null,topAtt=-1;
    Object.keys(memberMap).forEach(function(n){
      if(MEMBER_NAMES.indexOf(n)<0)return;
      if(memberMap[n].att>topAtt){topAtt=memberMap[n].att;top=n;}
    });
    elT.innerHTML=
      '<div class="st-tile"><div class="n">'+totalEvents+'</div><div class="u">크루대전</div></div>'
      +'<div class="st-tile"><div class="n">'+totalGames+'</div><div class="u">치른 게임</div></div>'
      +'<div class="st-tile"><div class="n">'+winRate+'%</div><div class="u">게임 승률</div><div class="s">'+totalWins+'승 '+(totalGames-totalWins)+'패</div></div>'
      +(top?'<div class="st-tile"><div class="n">'+esc(top)+'</div><div class="u">참여율 1위</div><div class="s">'+Math.round(topAtt/totalEvents*100)+'% 출전</div></div>':'');
    var mRows=Object.keys(memberMap).filter(function(n){return MEMBER_NAMES.indexOf(n)>=0;})
      .sort(function(a,b){
        if(memberMap[b].att!==memberMap[a].att)return memberMap[b].att-memberMap[a].att;
        return memberMap[b].win/memberMap[b].att-memberMap[a].win/memberMap[a].att;
      });
    elM.innerHTML=mRows.length?mRows.map(function(n){
      var s=memberMap[n],ap=Math.round(s.att/totalEvents*100),wp=s.att?Math.round(s.win/s.att*100):0;
      return '<div class="st-row"><span class="nm">'+esc(n)+'</span>'
        +bar(s.att,totalEvents-s.att)
        +'<span class="val">'+s.att+'회('+ap+'%) <span class="st-badge '+badgeCls(wp)+'">승률 '+wp+'%</span></span></div>';
    }).join(''):'<div class="st-empty">멤버 기록이 없습니다.</div>';
    var gNames=Object.keys(gameMap).sort(function(a,b){return (gameMap[b].w+gameMap[b].l)-(gameMap[a].w+gameMap[a].l);});
    elG.innerHTML=gNames.length?gNames.map(function(n){
      var s=gameMap[n];
      return '<div class="st-row"><span class="nm">'+esc(n)+'</span>'+bar(s.w,s.l)
        +'<span class="val">'+s.w+'승 '+s.l+'패</span></div>';
    }).join(''):'<div class="st-empty">게임 기록이 없습니다.</div>';
    var cKeys=Object.keys(crewMap).sort(function(a,b){return (crewMap[b].w+crewMap[b].l)-(crewMap[a].w+crewMap[a].l);});
    elC.innerHTML=cKeys.length?cKeys.map(function(k){
      var s=crewMap[k],t=s.w+s.l,p=t?Math.round(s.w/t*100):0;
      var title=s.past.length?' title="과거 이름: '+esc(s.past.join(' → '))+'"':'';
      return '<div class="st-row"><span class="nm"'+title+'>'+esc(s.name)+'</span>'+bar(s.w,s.l)
        +'<span class="val">'+s.w+'승 '+s.l+'패 <span class="st-badge '+badgeCls(p)+'">'+p+'%</span></span></div>';
    }).join(''):'<div class="st-empty">상대 크루 기록이 없습니다.</div>';
  }).catch(function(err){
    elM.innerHTML='<div class="st-empty">통계를 불러오지 못했습니다: '+esc(err&&err.message||err)+'</div>';
  });
})();</script>"""
    write("stats", "통계 · 전적", body, STATS_CSS, scripts=js)


# ---------- 아키타입: 최신 소식 (피드) ----------

NEWS_CSS = PAGE_CSS + """
.news-cols{display:grid;grid-template-columns:1fr 1fr;gap:clamp(20px,3vw,36px)}
@media(max-width:820px){.news-cols{grid-template-columns:1fr}}
.news-panel h3{margin:0 0 16px;font-size:20px;font-weight:900;letter-spacing:-.02em;display:flex;align-items:center;gap:8px}
.news-panel h3 a{margin-left:auto;font-size:13px;font-weight:700;color:var(--ink-2)}
.news-panel h3 a:hover{color:var(--accent)}
.news-row{display:flex;align-items:center;gap:12px;padding:13px 0;border-top:1px solid var(--line);cursor:pointer;transition:transform .15s}
.news-row:first-of-type{border-top:none}
.news-row:hover{transform:translateX(5px)}
.news-row .tag{flex:0 0 auto;font-size:10.5px;font-weight:800;padding:3px 8px;border-radius:999px;
  border-left:3px solid var(--tc);background:color-mix(in srgb,var(--tc) 20%,transparent);color:var(--ink)}
.news-row .t{flex:1 1 auto;font-size:14.5px;font-weight:700;word-break:keep-all}
.news-row .dt{flex:0 0 auto;font-size:12px;color:var(--ink-2)}
.news-hero{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:clamp(22px,3vw,34px);margin-bottom:clamp(28px,4vw,44px)}
.news-hero .k{font-size:12px;font-weight:800;letter-spacing:.16em;color:var(--accent);text-transform:uppercase}
.news-hero h2{margin:10px 0 12px;font-size:clamp(24px,3.4vw,40px);font-weight:900;letter-spacing:-.03em;word-break:keep-all}
.news-hero p{margin:0 0 18px;color:var(--ink-2);line-height:1.7;word-break:keep-all}
.news-empty{padding:14px 0;font-size:14px;color:var(--ink-2)}
"""


def build_news():
    # 07-11 런타임 전환(§2.5-3): 정적 시드 대신 WhaleData.list로 공지/클립/일정 실데이터 렌더.
    # 히어로 = 고정 공지 우선(없으면 최신 공지). 데이터 없으면 히어로 숨김 + 패널별 빈 문구.
    hero = ('<div class="news-hero img-ani bottom-top" id="newsHero" hidden><div class="k">HEADLINE</div>'
            '<h2 id="newsHeroTitle"></h2><p id="newsHeroBody"></p>'
            '<a class="btn primary sm" id="newsHeroLink" href="notices.html">자세히 보기 →</a></div>')

    body = (page_head_block("NEWS", "고래상사 메인", "최신 소식") + hero
            + '<div class="news-cols img-ani bottom-top">'
              '<div class="news-panel"><h3>📢 공지사항<a href="notices.html">전체 →</a></h3>'
              '<div id="newsN"><div class="news-empty">불러오는 중...</div></div></div>'
              '<div class="news-panel"><h3>🎬 새 클립<a href="clips.html">전체 →</a></h3>'
              '<div id="newsC"><div class="news-empty">불러오는 중...</div></div></div>'
              '</div>'
              '<div style="height:clamp(24px,3vw,36px)"></div>'
              '<div class="news-panel img-ani bottom-top"><h3>🗓 다가오는 방송<a href="schedule.html">캘린더 →</a></h3>'
              '<div id="newsS"><div class="news-empty">불러오는 중...</div></div></div>')

    js = """<script>(function(){
  var D=window.WhaleData;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var NC=""" + json.dumps(NOTICE_COLORS, ensure_ascii=False) + """;
  var TC=""" + json.dumps(TYPE_COLORS, ensure_ascii=False) + """;
  var elN=document.getElementById('newsN'), elC=document.getElementById('newsC'), elS=document.getElementById('newsS');
  var heroEl=document.getElementById('newsHero');
  function row(href,color,tag,title,dt){
    return '<div class="news-row" data-href="'+esc(href)+'" role="button" tabindex="0">'
      +'<span class="tag" style="--tc:'+(color||'#2f63ff')+'">'+esc(tag)+'</span>'
      +'<span class="t">'+esc(title)+'</span><span class="dt">'+esc(dt)+'</span></div>';
  }
  function empty(el,msg){el.innerHTML='<div class="news-empty">'+esc(msg)+'</div>';}
  function md(s){return (s||'').slice(5);}

  D.list('notices').then(function(items){
    if(!items.length){empty(elN,'등록된 공지가 없습니다.');return;}
    var byDate=items.slice().sort(function(a,b){return a.date<b.date?1:(a.date>b.date?-1:0);});
    var hn=items.filter(function(n){return n.pinned;})[0]||byDate[0];
    document.getElementById('newsHeroTitle').textContent=hn.title;
    document.getElementById('newsHeroBody').textContent=(hn.body&&hn.body[0])||'';
    document.getElementById('newsHeroLink').href='notice.html?id='+encodeURIComponent(hn.id);
    heroEl.hidden=false;
    elN.innerHTML=byDate.slice(0,5).map(function(n){
      return row('notice.html?id='+encodeURIComponent(n.id),NC[n.cat],n.cat,n.title,md(n.date));
    }).join('');
  }).catch(function(){empty(elN,'공지를 불러오지 못했습니다.');});

  D.list('clips').then(function(items){
    if(!items.length){empty(elC,'등록된 클립이 없습니다.');return;}
    var sorted=items.slice().sort(function(a,b){return (b.createdAt||0)-(a.createdAt||0);});
    elC.innerHTML=sorted.slice(0,5).map(function(c){
      var dt=c.createdAt?new Date(c.createdAt).toISOString().slice(5,10):'';
      return row('clip.html?id='+encodeURIComponent(c.id),'#0fb5b0',c.category||'클립',c.title,dt);
    }).join('');
  }).catch(function(){empty(elC,'클립을 불러오지 못했습니다.');});

  D.list('schedules').then(function(items){
    var today=new Date();today.setHours(0,0,0,0);
    var iso=today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');
    var up=items.filter(function(e){return e.date>=iso;}).sort(function(a,b){return a.date<b.date?-1:(a.date>b.date?1:0);});
    if(!up.length){empty(elS,items.length?'예정된 방송이 없습니다.':'등록된 일정이 없습니다.');return;}
    elS.innerHTML=up.slice(0,5).map(function(e){
      return row('schedule-detail.html?id='+encodeURIComponent(e.id),TC[e.type],e.type||'방송',e.title,md(e.date));
    }).join('');
  }).catch(function(){empty(elS,'일정을 불러오지 못했습니다.');});

  document.addEventListener('click',function(e){
    var r=e.target.closest&&e.target.closest('.news-row[data-href]');
    if(r)location.href=r.getAttribute('data-href');
  });
  document.addEventListener('keydown',function(e){
    if(e.key!=='Enter'&&e.key!==' ')return;
    var r=e.target.closest&&e.target.closest('.news-row[data-href]');
    if(r&&e.target===r){e.preventDefault();location.href=r.getAttribute('data-href');}
  });
})();</script>"""
    write("news", "최신 소식", body, NEWS_CSS, scripts=js)


def build():
    done = {"news", "crew", "members", "member", "clips", "clip", "archive", "archive-detail", "stats",
            "schedule", "schedule-detail", "notices", "notice", "multiview",
            "admin", "admin-login", "admin-clips", "admin-notices", "admin-members"}
    build_crew()
    build_members()
    build_member()
    build_clips()
    build_clip()
    build_archive()
    build_archive_detail()
    build_stats()
    build_schedule()
    build_schedule_detail()
    build_notices()
    build_notice()
    build_multiview()
    build_news()
    build_admin_dashboard()
    build_admin_login()
    build_admin_clips()
    build_admin_notices()
    build_admin_members()
    stub_count = 0
    for g in SITE["groups"]:
        for p in g["pages"]:
            if p["slug"] in done or p.get("home"):
                continue
            build_stub(p["slug"], g)
            stub_count += 1
    print(f"✅ 실구현 {len(done)}페이지 + 스텁 {stub_count}페이지 → {OUT}")


if __name__ == "__main__":
    build()
