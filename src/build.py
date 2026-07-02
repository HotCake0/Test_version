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

def head(title, page_css=""):
    css = f"<style>{page_css}</style>" if page_css else ""
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-store">
<title>{esc(title)} · 고래상사</title>
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
            f'<div class="grp-t" tabindex="0"><span class="mn">{g["no"]}</span>{esc(g["title"])}</div>'
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
              '<a href="../와이어프레임/index.html">와이어프레임</a>'
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
    doc = (head(title, page_css)
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
.mdetail .navrow{display:flex;gap:10px}
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


def clips_json_script():
    """pages/ 기준 WHALE_CLIPS 주입 (클립 상세 페이지용)."""
    data = []
    for c in CLIPS:
        d = dict(c)
        if d.get("img"):
            d["img"] = "../" + d["img"]
        data.append(d)
    return ('<script>window.WHALE_CLIPS=' +
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
          '<p>대표이사부터 신입사원까지, 회사 역할극이라는 하나의 세계관 안에서 각자의 자리를 맡아 매일 방송을 이어갑니다. '
          '게임·콘텐츠·영업·기획·방송… 부서는 달라도 \'웃음\'이라는 목표는 같습니다.</p>'
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
    write("members", "멤버 목록", body, PAGE_CSS,
          scripts=members_json_script() + filt + live, need_member_modal=True)


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
  function countUp(el,t){if(PRM){el.textContent=t.toLocaleString();return;}
    var s=null;(function step(ts){if(!s)s=ts;var p=Math.min((ts-s)/1200,1);
    el.textContent=Math.floor((1-Math.pow(1-p,3))*t).toLocaleString();
    if(p<1)requestAnimationFrame(step);})(performance.now());}
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function render(){
    var m=M[i];if(!m)return;
    document.title=m.name+' · 고래상사';
    var img=m.img?'<img src="'+esc(m.img)+'" alt="'+esc(m.name)+'" onerror="this.style.display=\\'none\\'">':'';
    var stats=(m.stats||[]).map(function(s,k){
      return '<div class="stat"><div class="n" id="ds'+k+'">0</div><div class="u">'+esc(s.u)+'</div></div>';}).join('');
    var el=document.getElementById('mDetail');
    el.innerHTML=
      '<div class="portrait" style="background:'+esc(m.color)+'">'+img+
        '<div class="ava-ph">'+esc(m.initials)+'</div></div>'+
      '<div><div class="dept-label">'+esc(m.dept)+'</div>'+
        '<h2>'+esc(m.name)+'</h2><div class="role">'+esc(m.role)+'</div>'+
        '<p class="bio">'+esc(m.bio)+'</p>'+
        '<div class="stats">'+stats+'</div>'+
        '<div class="navrow"><button class="btn sm" id="dPrev">← 이전 멤버</button>'+
        '<button class="btn sm" id="dNext">다음 멤버 →</button>'+
        '<a class="btn sm primary" href="members.html">전체 목록</a></div></div>';
    (m.stats||[]).forEach(function(s,k){var e=document.getElementById('ds'+k);if(e)countUp(e,s.n);});
    document.getElementById('dPrev').onclick=function(){i=(i-1+M.length)%M.length;render();};
    document.getElementById('dNext').onclick=function(){i=(i+1)%M.length;render();};
  }
  render();
})();</script>"""
    write("member", "멤버 상세", body, PAGE_CSS,
          scripts=members_json_script() + render)


# ---------- 아키타입: 클립 ----------

def build_clips():
    """클립 갤러리 (clips). 대표 클립 히어로 + 카테고리 필터 + 16:9 카드 그리드."""
    # 대표 클립 탐색
    feat_i, feat = next(
        ((i, c) for i, c in enumerate(CLIPS) if c.get("featured")),
        (0, CLIPS[0]))

    # 대표 클립 썸네일 내용
    if feat.get("img"):
        feat_bg = (f'<img src="../{esc(feat["img"])}" alt="{esc(feat["title"])}" '
                   f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;"'
                   f' onerror="this.style.display=\'none\'">')
    else:
        feat_bg = f'<div style="position:absolute;inset:0;background:{esc(feat.get("grad","#0f1730"))}"></div>'

    views_n = feat.get("views", 0)
    views_feat = f'{views_n/10000:.1f}만' if views_n >= 10000 else f'{views_n:,}'

    feat_html = (
        '<section class="clips-hero img-ani bottom-top">'
        f'<a class="orig-feat" href="clip.html?i={feat_i}" aria-label="{esc(feat["title"])} 시청">'
        + feat_bg +
        '<div class="orig-play" aria-hidden="true">▶</div></a>'
        '<div class="clips-hero-info">'
        f'<div class="ch-cat">{esc(feat["category"])} · 대표 클립</div>'
        f'<p class="ch-title">{esc(feat["title"])}</p>'
        '<div class="ch-meta">'
        f'<span>제작: {esc(feat["creator"])}</span>'
        f'<span>{esc(feat["date"])}</span>'
        f'<span class="ch-dur">{esc(feat["duration"])}</span>'
        f'<span>{views_feat} 조회</span>'
        '</div>'
        f'<p class="ch-desc">{esc(feat.get("desc",""))}</p>'
        f'<a class="btn primary" href="clip.html?i={feat_i}">▶ 클립 시청</a>'
        '</div></section>')

    # 카테고리 목록
    cats = []
    for c in CLIPS:
        if c["category"] not in cats:
            cats.append(c["category"])
    chips = ('<button class="chip active" data-f="all">전체</button>'
             + "".join(
                 f'<button class="chip" data-f="{esc(cat)}">{esc(cat)}</button>'
                 for cat in cats))

    # 카드 그리드
    def clip_card(c, idx):
        if c.get("img"):
            thumb_inner = (
                f'<img src="../{esc(c["img"])}" alt="{esc(c["title"])}"'
                f' onerror="this.style.display=\'none\'">')
        else:
            thumb_inner = (
                f'<div class="ccard-grad"'
                f' style="background:{esc(c.get("grad","#0f1730"))}"></div>')
        v = c.get("views", 0)
        v_str = f'{v/10000:.1f}만' if v >= 10000 else f'{v:,}'
        return (
            f'<article class="ccard img-ani bottom-top" data-i="{idx}"'
            f' data-cat="{esc(c["category"])}"'
            f' role="button" tabindex="0" aria-label="{esc(c["title"])} 클립 시청">'
            f'<div class="ccard-thumb">{thumb_inner}'
            f'<div class="cplay" aria-hidden="true">▶</div></div>'
            f'<div class="ccard-info">'
            f'<div class="ccard-title">{esc(c["title"])}</div>'
            f'<div class="ccard-meta">'
            f'<span>{esc(c["creator"])}</span>'
            f'<span class="ccard-dur">{esc(c["duration"])}</span>'
            f'<span>{v_str} 조회</span>'
            f'</div></div></article>')

    cards = "".join(clip_card(c, i) for i, c in enumerate(CLIPS))

    body = (
        page_head_block("CLIPS", "베스트 클립", "베스트 클립")
        + feat_html
        + f'<div class="pg-tools img-ani bottom-top">{chips}'
          f'<span class="pg-count" id="cCount">전체 {len(CLIPS)}개</span></div>'
        + f'<div class="cgrid" id="cGrid">{cards}</div>')

    filt = """<script>(function(){
  var chips=[].slice.call(document.querySelectorAll('.chip[data-f]'));
  var cards=[].slice.call(document.querySelectorAll('#cGrid .ccard'));
  var count=document.getElementById('cCount');
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('active')});
    c.classList.add('active');
    var f=c.getAttribute('data-f'),n=0;
    cards.forEach(function(card){
      var show=f==='all'||card.getAttribute('data-cat')===f;
      card.style.display=show?'':'none';if(show)n++;
    });
    count.textContent=(f==='all'?'전체':f)+' '+n+'개';
  });});
  cards.forEach(function(card){
    card.addEventListener('click',function(){
      location.href='clip.html?i='+this.getAttribute('data-i');
    });
    card.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' ')location.href='clip.html?i='+this.getAttribute('data-i');
    });
  });
})();</script>"""

    write("clips", "베스트 클립", body, PAGE_CSS, scripts=filt)


def build_clip():
    """클립 시청 상세 (clip). ?i=인덱스로 클라이언트 렌더 — build_member() 패턴 모방."""
    body = (
        page_head_block("CLIPS", "베스트 클립", "클립 시청")
        + '<div class="cdetail img-ani bottom-top" id="cDetail"></div>')

    render = """<script>(function(){
  var C=window.WHALE_CLIPS||[];
  var i=parseInt(new URLSearchParams(location.search).get('i')||'0',10);
  if(isNaN(i)||i<0||i>=C.length)i=0;
  function fmtViews(n){
    if(!n)return'0';
    return n>=10000?(n/10000).toFixed(1)+'만':n.toLocaleString();
  }
  function escT(x){
    var d=document.createElement('div');d.textContent=x==null?'':String(x);return d.innerHTML.replace(/"/g,'&quot;');
  }
  function render(){
    var c=C[i];if(!c)return;
    document.title=c.title+' · 고래상사';
    var bgInner=c.img
      ?'<img src="'+escT(c.img)+'" alt="'+escT(c.title)+'" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" onerror="this.style.display=\\'none\\'">'
      :'<div style="position:absolute;inset:0;background:'+escT(c.grad||'#0f1730')+'"></div>';
    var rel=[];
    C.forEach(function(r,j){if(j!==i&&rel.length<5)rel.push(j);});
    var relHtml=rel.map(function(j){
      return '<li><a class="orig-item" href="clip.html?i='+j+'" data-j="'+j+'">'
        +'<span class="oi-t">'+escT(C[j].title)+'</span>'
        +'<span class="oi-ar">↗</span></a></li>';
    }).join('');
    var el=document.getElementById('cDetail');
    el.innerHTML=
      '<div class="cdetail-player">'+bgInner
        +'<div class="orig-play" aria-hidden="true">▶</div></div>'
      +'<div class="cm-cat">'+escT(c.category)+'</div>'
      +'<h2 class="cdetail-title">'+escT(c.title)+'</h2>'
      +'<div class="cdetail-meta">'
        +'<span>제작: '+escT(c.creator)+'</span>'
        +'<span>'+escT(c.date)+'</span>'
        +'<span class="ccard-dur">'+escT(c.duration)+'</span>'
        +'<span>'+fmtViews(c.views)+' 조회</span>'
      +'</div>'
      +'<p class="cdetail-desc">'+escT(c.desc||'')+'</p>'
      +'<div class="cdetail-nav">'
        +'<button class="btn sm" id="cPrev">← 이전 클립</button>'
        +'<button class="btn sm" id="cNext">다음 클립 →</button>'
        +'<a class="btn sm primary" href="clips.html">전체 클립</a>'
      +'</div>'
      +(rel.length?'<div class="crelated-head">관련 클립</div><ul class="orig-list">'+relHtml+'</ul>':'');
    document.getElementById('cPrev').onclick=function(){
      i=(i-1+C.length)%C.length;render();history.replaceState(null,'','?i='+i);
    };
    document.getElementById('cNext').onclick=function(){
      i=(i+1)%C.length;render();history.replaceState(null,'','?i='+i);
    };
    [].forEach.call(el.querySelectorAll('.orig-item[data-j]'),function(a){
      a.onclick=function(e){
        e.preventDefault();
        i=parseInt(this.getAttribute('data-j'),10);
        render();history.replaceState(null,'','?i='+i);
      };
    });
  }
  render();
})();</script>"""

    write("clip", "클립 시청", body, PAGE_CSS, scripts=clips_json_script() + render)


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


# ---------- 아카이브: 통합 목록 + 상세 ----------

def build_archive():
    """크루대전 기록 아카이브 — 라이브 Firebase /contests.json 실시간 로드."""
    inject = ('<script>window.FB="https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app";</script>')
    body = (page_head_block("ARCHIVE", "콘텐츠 아카이브", "크루대전 기록")
            + '<div class="pg-tools img-ani bottom-top">'
              '<button class="chip active" data-f="all">전체</button>'
              '<button class="chip" data-f="win">🏆 우승</button>'
              '<button class="chip" data-f="join">참가</button>'
              '<span class="pg-count" id="aCount"></span></div>'
            + '<div class="agrid img-ani bottom-top" id="aGrid">'
              '<div class="stub" style="grid-column:1/-1"><p>대회 기록을 불러오는 중…</p></div></div>')
    js = r"""<script>(function(){
  var FB=window.FB,grid=document.getElementById('aGrid'),count=document.getElementById('aCount');
  var all=[],filt='all';
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function wl(c){var w=0,l=0,g=c.games||{};Object.keys(g).forEach(function(k){g[k].result?w++:l++;});return {w:w,l:l};}
  function card(c){
    var r=wl(c),win=c.rank===1;
    var cast=(c.members||[]).slice(0,6).map(function(m){return '<span class="ct-chip">'+esc(m)+'</span>';}).join('');
    var more=(c.members||[]).length>6?'<span class="ct-chip">+'+((c.members||[]).length-6)+'</span>':'';
    return '<a class="ct-card" href="archive-detail.html?id='+encodeURIComponent(c._id)+'">'
      +'<div class="ct-top"><span class="ct-rank '+(win?'win':'lose')+'">'
        +(win?'🏆 우승':(c.rank?c.rank+'위':'참가'))+'</span>'
      +'<span class="ct-date">'+esc(c.date||'')+'</span></div>'
      +'<div class="ct-title">'+esc(c.title||'제목 없음')+'</div>'
      +'<div class="ct-meta"><span class="ct-wl">전적 <span class="w">'+r.w+'승</span> <span class="l">'+r.l+'패</span></span>'
      +'<span>'+(c.total_teams?c.total_teams+'팀 참가':'')+'</span></div>'
      +'<div class="ct-cast">'+cast+more+'</div></a>';
  }
  function render(){
    var arr=all.filter(function(c){
      if(filt==='win')return c.rank===1;
      if(filt==='join')return c.rank!==1;return true;});
    count.textContent=arr.length+'개 대회';
    grid.innerHTML=arr.length?arr.map(card).join(''):'<div class="stub" style="grid-column:1/-1"><p>해당 기록이 없습니다.</p></div>';
  }
  [].forEach.call(document.querySelectorAll('.chip[data-f]'),function(c){c.addEventListener('click',function(){
    document.querySelectorAll('.chip[data-f]').forEach(function(x){x.classList.remove('active')});
    c.classList.add('active');filt=c.getAttribute('data-f');render();});});
  fetch(FB+'/contests.json?v='+Date.now()).then(function(r){return r.json();}).then(function(d){
    d=d||{};all=Object.keys(d).map(function(k){var o=d[k];o._id=k;return o;})
      .sort(function(a,b){return (a.date<b.date?1:a.date>b.date?-1:0);});
    render();
  }).catch(function(){grid.innerHTML='<div class="stub" style="grid-column:1/-1"><p>기록을 불러오지 못했습니다.</p></div>';});
})();</script>"""
    write("archive", "크루대전 기록", body, ARCHIVE_CSS, scripts=inject + js)


def build_archive_detail():
    """대회 상세 — ?id=Firebase키 로 /contests/{id}.json 실시간 로드."""
    inject = ('<script>window.FB="https://whaie-corp-default-rtdb.asia-southeast1.firebasedatabase.app";</script>')
    body = (page_head_block("ARCHIVE", "콘텐츠 아카이브", "대회 상세")
            + '<div class="img-ani bottom-top" id="cDetail"><div class="stub"><p>불러오는 중…</p></div></div>')
    js = r"""<script>(function(){
  var FB=window.FB,id=new URLSearchParams(location.search).get('id');
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var el=document.getElementById('cDetail');
  if(!id){el.innerHTML='<div class="stub"><p>잘못된 접근입니다.</p><a class="btn primary" href="archive.html">목록으로</a></div>';return;}
  fetch(FB+'/contests/'+encodeURIComponent(id)+'.json?v='+Date.now()).then(function(r){return r.json();}).then(function(c){
    if(!c){el.innerHTML='<div class="stub"><p>기록을 찾을 수 없습니다.</p></div>';return;}
    document.title=(c.title||'대회 상세')+' · 고래상사';
    var win=c.rank===1;
    var g=c.games||{},games=Object.keys(g).map(function(k){var x=g[k];
      return '<div class="cd-game"><span>'+esc(x.name)+'</span><span class="cd-res '+(x.result?'w':'l')+'">'+(x.result?'승':'패')+'</span></div>';}).join('');
    var opp=(c.opponents||[]).map(function(o){return '<span class="op">'+esc(o.name)+(o.result===false?' <span style=color:var(--accent)>승</span>':o.result===true?' <span style=color:var(--hot)>패</span>':'')+'</span>';}).join('');
    var vids=(c.videos||[]).map(function(v){return '<a class="btn sm primary" href="'+esc(v.url)+'" target="_blank" rel="noopener">▶ '+esc(v.label||'영상')+'</a>';}).join('');
    var cast=(c.members||[]).map(function(m){return '<span class="ct-chip">'+esc(m)+'</span>';}).join('');
    el.innerHTML=
      '<div class="ct-top" style="margin-bottom:14px"><span class="ct-rank '+(win?'win':'lose')+'">'+(win?'🏆 우승':(c.rank?c.rank+'위':'참가'))+'</span>'
        +'<span class="ct-date">'+esc(c.date||'')+(c.total_teams?' · '+c.total_teams+'팀':'')+'</span></div>'
      +'<h2 class="adetail-title">'+esc(c.title||'')+'</h2>'
      +(vids?'<div class="cd-vids">'+vids+'</div>':'')
      +(opp?'<h3 class="cd-h">상대 크루</h3><div class="cd-opp">'+opp+'</div>':'')
      +(games?'<h3 class="cd-h" style="margin-top:22px">경기 결과</h3><div class="cd-games">'+games+'</div>':'')
      +'<h3 class="cd-h">참가 멤버</h3><div class="ct-cast" style="margin-bottom:26px">'+cast+'</div>'
      +(c.notes?'<p class="adetail-desc">'+esc(c.notes)+'</p>':'')
      +'<div class="adetail-nav"><a class="btn sm primary" href="archive.html">← 전체 기록</a></div>';
  }).catch(function(){el.innerHTML='<div class="stub"><p>불러오지 못했습니다.</p></div>';});
})();</script>"""
    write("archive-detail", "대회 상세", body, ARCHIVE_CSS, scripts=inject + js)


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
.slist .sched-row{cursor:pointer;transition:padding-left .15s}
.slist .sched-row:hover{padding-left:6px}
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


def schedule_json_script():
    data = []
    for i, e in enumerate(SCHEDULE):
        d = dict(e); d["i"] = i
        d["tc"] = TYPE_COLORS.get(e.get("type"), "#2f63ff")
        data.append(d)
    return ('<script>window.WHALE_SCHEDULE=' + json.dumps(data, ensure_ascii=False) + ';</script>')


def build_schedule():
    body = (
        page_head_block("SCHEDULE", "방송 일정", "일정 캘린더")
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
        + '<div id="listView" class="slist img-ani bottom-top" style="display:none"></div>')

    js = """<script>(function(){
  var S=window.WHALE_SCHEDULE||[];
  var byDate={};S.forEach(function(e){(byDate[e.date]=byDate[e.date]||[]).push(e);});
  var now=new Date();
  var cur=new Date(now.getFullYear(),now.getMonth(),1);
  var todayISO=(function(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);})();
  var grid=document.getElementById('calGrid'),title=document.getElementById('calTitle');
  function iso(y,m,d){return y+'-'+('0'+(m+1)).slice(-2)+'-'+('0'+d).slice(-2);}
  function evChip(e){
    return '<div class="cal-ev" style="--tc:'+e.tc+'" role="button" tabindex="0" '
      +'data-i="'+e.i+'" title="'+esc(e.time)+' '+esc(e.title)+'">'+esc(e.title)+'</div>';
  }
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function render(){
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
      var go=function(){location.href='schedule-detail.html?i='+el.getAttribute('data-i');};
      el.addEventListener('click',go);
      el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
    });
  }
  document.getElementById('calPrev').onclick=function(){cur.setMonth(cur.getMonth()-1);render();};
  document.getElementById('calNext').onclick=function(){cur.setMonth(cur.getMonth()+1);render();};
  render();
  // 목록 뷰
  var lv=document.getElementById('listView');
  var sorted=S.slice().sort(function(a,b){return a.date<b.date?-1:a.date>b.date?1:0;});
  var W=['일','월','화','수','목','금','토'];
  lv.innerHTML=sorted.map(function(e){
    var dt=new Date(e.date+'T00:00:00');
    var badge=(e.date.slice(5).replace('-','.'))+' ('+W[dt.getDay()]+')';
    var cast=(e.members||[]).join(', ');
    return '<div class="sched-row" data-i="'+e.i+'" role="button" tabindex="0">'
      +'<span class="day" style="--tc:'+e.tc+';background:'+e.tc+'">'+badge+'</span>'
      +'<span class="desc"><b>'+e.time+'</b> — '+esc(e.title)
      +'<span class="stype" style="--tc:'+e.tc+'">'+esc(e.type)+'</span>'
      +'<br><span style="color:var(--ink-2);font-size:12.5px">'+esc(cast)+'</span></span></div>';
  }).join('');
  [].forEach.call(lv.querySelectorAll('.sched-row'),function(el){
    var go=function(){location.href='schedule-detail.html?i='+el.getAttribute('data-i');};
    el.addEventListener('click',go);
    el.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();go();}});
  });
  // 뷰 토글
  var chips=[].slice.call(document.querySelectorAll('.sview .chip'));
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('active')});c.classList.add('active');
    var v=c.getAttribute('data-v');
    document.getElementById('calView').style.display=v==='cal'?'':'none';
    lv.style.display=v==='list'?'':'none';
  });});
})();</script>"""
    write("schedule", "일정 캘린더", body, SCHEDULE_CSS, scripts=schedule_json_script() + js)


def build_schedule_detail():
    body = (page_head_block("SCHEDULE", "방송 일정", "일정 상세")
            + '<div class="img-ani bottom-top" id="sDetail"></div>')
    js = """<script>(function(){
  var S=window.WHALE_SCHEDULE||[];
  var i=parseInt(new URLSearchParams(location.search).get('i')||'0',10);
  if(isNaN(i)||i<0||i>=S.length)i=0;
  var W=['일','월','화','수','목','금','토'];
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function render(){
    var e=S[i];if(!e)return;document.title=e.title+' · 고래상사';
    var dt=new Date(e.date+'T00:00:00');
    var dateStr=e.date.replace(/-/g,'.')+' ('+W[dt.getDay()]+') '+e.time;
    var cast=(e.members||[]).map(function(m){return '<span class="mchip">'+esc(m)+'</span>';}).join('');
    var rel=S.filter(function(x){return x.i!==e.i&&(x.type===e.type||x.date===e.date);}).slice(0,4);
    var relH=rel.map(function(x){
      return '<li><a class="orig-item" href="schedule-detail.html?i='+x.i+'">'
        +'<span class="oi-t">'+esc(x.date.slice(5).replace('-','.'))+' · '+esc(x.title)+'</span>'
        +'<span class="oi-ar" aria-hidden="true">↗</span></a></li>';}).join('');
    document.getElementById('sDetail').innerHTML=
      '<div class="cm-cat" style="color:'+e.tc+'">'+esc(e.type)+'</div>'
      +'<h2 class="adetail-title" style="font-size:clamp(28px,4vw,52px);font-weight:900;letter-spacing:-.03em;margin:6px 0 0">'+esc(e.title)+'</h2>'
      +'<div class="sdetail-meta"><span>🗓 '+esc(dateStr)+'</span></div>'
      +'<div class="sdetail-cast">'+cast+'</div>'
      +'<p class="sdetail-desc">'+esc(e.desc||'')+'</p>'
      +'<div class="sdetail-nav"><button class="btn sm" id="sPrev">← 이전 일정</button>'
      +'<button class="btn sm" id="sNext">다음 일정 →</button>'
      +'<a class="btn sm primary" href="schedule.html">전체 일정</a></div>'
      +(relH?'<div class="crelated-head" style="margin-top:40px;font-weight:900;font-size:18px">관련 일정</div><ul class="orig-list">'+relH+'</ul>':'');
    document.getElementById('sPrev').onclick=function(){i=(i-1+S.length)%S.length;render();};
    document.getElementById('sNext').onclick=function(){i=(i+1)%S.length;render();};
  }
  render();
})();</script>"""
    write("schedule-detail", "일정 상세", body, SCHEDULE_CSS, scripts=schedule_json_script() + js)


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
.ndetail-nav{display:flex;gap:10px;margin-top:36px;border-top:1px solid var(--line);padding-top:26px}
@media(max-width:640px){.nrow{flex-wrap:wrap;gap:8px}.ntitle{flex:1 1 100%;order:3}}
"""

NOTICE_COLORS = {"공지": "#2f63ff", "이벤트": "#ff3d92", "업데이트": "#0fb5b0", "점검": "#ffcb45"}


def notices_json_script():
    data = []
    for i, n in enumerate(NOTICES):
        d = dict(n); d["i"] = i; d["tc"] = NOTICE_COLORS.get(n.get("cat"), "#2f63ff")
        data.append(d)
    return '<script>window.WHALE_NOTICES=' + json.dumps(data, ensure_ascii=False) + ';</script>'


def build_notices():
    cats = []
    for n in NOTICES:
        if n["cat"] not in cats:
            cats.append(n["cat"])
    chips = ('<button class="chip active" data-f="all">전체</button>'
             + "".join(f'<button class="chip" data-f="{esc(c)}">{esc(c)}</button>' for c in cats))
    body = (page_head_block("NOTICE", "공지사항", "공지사항")
            + f'<div class="pg-tools img-ani bottom-top">{chips}'
              f'<span class="pg-count" id="nCount">전체 {len(NOTICES)}건</span></div>'
            + '<div class="nlist img-ani bottom-top" id="nList"></div>')
    js = """<script>(function(){
  var N=window.WHALE_NOTICES||[];
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  var sorted=N.slice().sort(function(a,b){
    if(a.pinned!==b.pinned)return a.pinned?-1:1;return a.date<b.date?1:-1;});
  var list=document.getElementById('nList');
  list.innerHTML=sorted.map(function(n){
    return '<div class="nrow" data-cat="'+esc(n.cat)+'" data-i="'+n.i+'" role="button" tabindex="0">'
      +(n.pinned?'<span class="npin" title="상단 고정">📌</span>':'')
      +'<span class="ncat" style="--tc:'+n.tc+'">'+esc(n.cat)+'</span>'
      +'<span class="ntitle">'+esc(n.title)+'</span>'
      +'<span class="ndate">'+esc(n.date)+'</span>'
      +'<span class="narrow" aria-hidden="true">→</span></div>';
  }).join('');
  var rows=[].slice.call(list.querySelectorAll('.nrow'));
  rows.forEach(function(el){
    var go=function(){location.href='notice.html?i='+el.getAttribute('data-i');};
    el.addEventListener('click',go);
    el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
  });
  var chips=[].slice.call(document.querySelectorAll('.chip[data-f]')),count=document.getElementById('nCount');
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('active')});c.classList.add('active');
    var f=c.getAttribute('data-f'),k=0;
    rows.forEach(function(r){var s=f==='all'||r.getAttribute('data-cat')===f;r.style.display=s?'':'none';if(s)k++;});
    count.textContent=(f==='all'?'전체':f)+' '+k+'건';
  });});
})();</script>"""
    write("notices", "공지사항", body, NOTICE_CSS, scripts=notices_json_script() + js)


def build_notice():
    body = (page_head_block("NOTICE", "공지사항", "공지 상세")
            + '<article class="img-ani bottom-top" id="nDetail"></article>')
    js = """<script>(function(){
  var N=window.WHALE_NOTICES||[];
  var i=parseInt(new URLSearchParams(location.search).get('i')||'0',10);
  if(isNaN(i)||i<0||i>=N.length)i=0;
  function esc(x){var d=document.createElement('div');d.textContent=x==null?'':x;return d.innerHTML.replace(/"/g,'&quot;');}
  function render(){
    var n=N[i];if(!n)return;document.title=n.title+' · 고래상사';
    var paras=(n.body||[]).map(function(p){return '<p>'+esc(p)+'</p>';}).join('');
    document.getElementById('nDetail').innerHTML=
      '<span class="ndetail-cat" style="--tc:'+n.tc+'">'+esc(n.cat)+'</span>'
      +'<h2 class="ndetail-title">'+(n.pinned?'📌 ':'')+esc(n.title)+'</h2>'
      +'<div class="ndetail-date">'+esc(n.date)+'</div>'
      +'<div class="ndetail-body">'+paras+'</div>'
      +'<div class="ndetail-nav"><button class="btn sm" id="nPrev">← 이전 글</button>'
      +'<button class="btn sm" id="nNext">다음 글 →</button>'
      +'<a class="btn sm primary" href="notices.html">목록으로</a></div>';
    document.getElementById('nPrev').onclick=function(){i=(i-1+N.length)%N.length;render();};
    document.getElementById('nNext').onclick=function(){i=(i+1)%N.length;render();};
  }
  render();
})();</script>"""
    write("notice", "공지 상세", body, NOTICE_CSS, scripts=notices_json_script() + js)


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
  sync();setInterval(sync,1000);
  var lb=document.getElementById('admLogin');
  if(lb)lb.addEventListener('click',function(){var b=document.getElementById('loginBtn');if(b)b.click();});
  [].forEach.call(document.querySelectorAll('[data-demo]'),function(el){
    el.addEventListener('click',function(){alert('데모 환경입니다. 실제 저장/수정은 Firebase 연동 후 활성화됩니다.');});
  });
})();</script>"""


def admin_gate(inner):
    return ('<div class="adm-gate" id="admGate" hidden><div class="lock">🔒</div>'
            '<h2>관리자 전용 페이지</h2>'
            '<p>이 페이지는 숲(SOOP) 관리자 권한이 필요합니다.<br>상단 로그인 버튼으로 인증해 주세요.</p>'
            '<button class="btn primary" id="admLogin">관리자 로그인</button></div>'
            f'<div class="adm-body" id="admBody" hidden>{inner}</div>')


def build_admin_dashboard():
    inner = (
        '<div class="adm-note">⚠️ 데모 환경입니다. 표시 데이터는 시드이며, 저장/수정 기능은 Firebase 연동 후 활성화됩니다.</div>'
        '<div class="adm-stats">'
        f'<div class="adm-stat"><div class="n">{len(MEMBERS)}</div><div class="u">멤버</div></div>'
        f'<div class="adm-stat"><div class="n">{len(CLIPS)}</div><div class="u">클립</div></div>'
        f'<div class="adm-stat"><div class="n">{len(ARCHIVE)}</div><div class="u">아카이브</div></div>'
        f'<div class="adm-stat"><div class="n">{len(SCHEDULE)}</div><div class="u">일정</div></div>'
        f'<div class="adm-stat"><div class="n">{len(NOTICES)}</div><div class="u">공지</div></div>'
        '</div>'
        '<div class="adm-quick">'
        '<a href="admin-clips.html"><span class="ic">🎬</span><span class="t">클립 관리</span><span class="d">베스트 클립 등록·수정·삭제</span></a>'
        '<a href="admin-notices.html"><span class="ic">📢</span><span class="t">공지/일정 관리</span><span class="d">공지사항·방송 일정 관리</span></a>'
        '<a href="admin-members.html"><span class="ic">👥</span><span class="t">멤버/크루 관리</span><span class="d">멤버 정보·직급 관리</span></a>'
        '</div>')
    body = page_head_block("ADMIN", "관리자 전용", "관리자 홈") + admin_gate(inner)
    write("admin", "관리자 홈", body, ADMIN_CSS, scripts=ADMIN_GATE_JS)


def build_admin_login():
    inner = (
        '<div class="adm-note">관리자 권한은 숲(SOOP) 계정으로 확인됩니다. 아래 버튼 또는 상단 로그인으로 인증하세요.</div>'
        '<div style="max-width:420px"><button class="btn primary" id="admLogin2" style="width:100%;justify-content:center;padding:14px">🔵 숲(SOOP) 계정으로 로그인</button>'
        '<p style="color:var(--ink-2);font-size:13px;margin-top:16px;line-height:1.7">권한 계정만 접근할 수 있습니다. '
        '관리자(admin)는 전체 관리, 편집자(editor)는 일정·공지 관리가 가능합니다.</p></div>')
    # 로그인 페이지는 게이트 없이 항상 로그인 유도
    body = (page_head_block("ADMIN", "관리자 전용", "로그인")
            + '<div class="adm-note">⚠️ 데모 — 로컬에서는 상단 로그인의 "개발용 로그인"으로 닉네임 권한을 조회해 테스트하세요.</div>'
            + inner)
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


# ---------- 아키타입: 최신 소식 (피드) ----------

NEWS_CSS = PAGE_CSS + """
.news-cols{display:grid;grid-template-columns:1fr 1fr;gap:clamp(20px,3vw,36px)}
@media(max-width:820px){.news-cols{grid-template-columns:1fr}}
.news-panel h3{margin:0 0 16px;font-size:20px;font-weight:900;letter-spacing:-.02em;display:flex;align-items:center;gap:8px}
.news-panel h3 a{margin-left:auto;font-size:13px;font-weight:700;color:var(--ink-2)}
.news-panel h3 a:hover{color:var(--accent)}
.news-row{display:flex;align-items:center;gap:12px;padding:13px 0;border-top:1px solid var(--line);cursor:pointer;transition:padding-left .15s}
.news-row:first-of-type{border-top:none}
.news-row:hover{padding-left:5px}
.news-row .tag{flex:0 0 auto;font-size:10.5px;font-weight:800;padding:3px 8px;border-radius:999px;
  border-left:3px solid var(--tc);background:color-mix(in srgb,var(--tc) 20%,transparent);color:var(--ink)}
.news-row .t{flex:1 1 auto;font-size:14.5px;font-weight:700;word-break:keep-all}
.news-row .dt{flex:0 0 auto;font-size:12px;color:var(--ink-2)}
.news-hero{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:clamp(22px,3vw,34px);margin-bottom:clamp(28px,4vw,44px)}
.news-hero .k{font-size:12px;font-weight:800;letter-spacing:.16em;color:var(--accent);text-transform:uppercase}
.news-hero h2{margin:10px 0 12px;font-size:clamp(24px,3.4vw,40px);font-weight:900;letter-spacing:-.03em;word-break:keep-all}
.news-hero p{margin:0 0 18px;color:var(--ink-2);line-height:1.7;word-break:keep-all}
"""


def build_news():
    notices_sorted = sorted(enumerate(NOTICES),
                            key=lambda t: (not t[1].get("pinned"), t[1]["date"]), reverse=False)
    notices_sorted = sorted(notices_sorted, key=lambda t: (0 if t[1].get("pinned") else 1, ),)
    # 히어로 = 고정 공지 첫 번째
    pinned = next((i for i, n in enumerate(NOTICES) if n.get("pinned")), 0)
    hn = NOTICES[pinned]
    hero = ('<div class="news-hero img-ani bottom-top"><div class="k">HEADLINE</div>'
            f'<h2>{esc(hn["title"])}</h2><p>{esc(hn["body"][0])}</p>'
            f'<a class="btn primary sm" href="notice.html?i={pinned}">자세히 보기 →</a></div>')

    ncol = "".join(
        f'<div class="news-row" onclick="location.href=\'notice.html?i={i}\'" role="button" tabindex="0">'
        f'<span class="tag" style="--tc:{NOTICE_COLORS.get(n["cat"],"#2f63ff")}">{esc(n["cat"])}</span>'
        f'<span class="t">{esc(n["title"])}</span><span class="dt">{esc(n["date"][5:])}</span></div>'
        for i, n in sorted(enumerate(NOTICES), key=lambda t: t[1]["date"], reverse=True)[:5])

    ccol = "".join(
        f'<div class="news-row" onclick="location.href=\'clip.html?i={i}\'" role="button" tabindex="0">'
        f'<span class="tag" style="--tc:#0fb5b0">{esc(c["category"])}</span>'
        f'<span class="t">{esc(c["title"])}</span><span class="dt">{esc(c.get("date","")[5:])}</span></div>'
        for i, c in list(enumerate(CLIPS))[:5])

    scol = "".join(
        f'<div class="news-row" onclick="location.href=\'schedule-detail.html?i={i}\'" role="button" tabindex="0">'
        f'<span class="tag" style="--tc:{TYPE_COLORS.get(e["type"],"#2f63ff")}">{esc(e["type"])}</span>'
        f'<span class="t">{esc(e["title"])}</span><span class="dt">{esc(e["date"][5:])}</span></div>'
        for i, e in sorted(enumerate(SCHEDULE), key=lambda t: t[1]["date"])[:5])

    body = (page_head_block("NEWS", "고래상사 메인", "최신 소식") + hero
            + '<div class="news-cols img-ani bottom-top">'
              f'<div class="news-panel"><h3>📢 공지사항<a href="notices.html">전체 →</a></h3>{ncol}</div>'
              f'<div class="news-panel"><h3>🎬 새 클립<a href="clips.html">전체 →</a></h3>{ccol}</div>'
              '</div>'
              '<div style="height:clamp(24px,3vw,36px)"></div>'
              f'<div class="news-panel img-ani bottom-top"><h3>🗓 다가오는 방송<a href="schedule.html">캘린더 →</a></h3>{scol}</div>')
    write("news", "최신 소식", body, NEWS_CSS)


def build():
    done = {"news", "crew", "members", "member", "clips", "clip", "archive", "archive-detail",
            "schedule", "schedule-detail", "notices", "notice", "multiview",
            "admin", "admin-login", "admin-clips", "admin-notices", "admin-members"}
    build_crew()
    build_members()
    build_member()
    build_clips()
    build_clip()
    build_archive()
    build_archive_detail()
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
