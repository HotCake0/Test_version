#!/usr/bin/env python3
# manyfast 와이어프레임 JSON(src/data/*.json) -> 정적 HTML(와이어프레임/*.html) 변환기
# 고래상사 리워크 버전 — 다크·글래스·네온 디자인 시스템 적용
import json, glob, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..", "와이어프레임")

SIZE_CLASS = {"xl": "t-xl", "lg": "t-lg", "md": "t-md", "sm": "t-sm", "xs": "t-xs"}


def esc(s):
    return html.escape(s or "")


def style_from_layout(layout):
    s = []
    if not layout:
        return ""
    gap = layout.get("gap")
    if gap is not None:
        s.append(f"gap:{gap}px")
    align = layout.get("align")
    amap = {"start": "flex-start", "center": "center", "end": "flex-end"}
    if align:
        s.append(f"align-items:{amap.get(align, align)}")
    justify = layout.get("justify")
    jmap = {"start": "flex-start", "center": "center", "end": "flex-end",
            "between": "space-between", "around": "space-around"}
    if justify:
        s.append(f"justify-content:{jmap.get(justify, justify)}")
    h = layout.get("height")
    if h is not None:
        s.append(f"min-height:{h}px")
    w = layout.get("width")
    if w is not None:
        s.append(f"max-width:{w}px;width:100%")
    return ";".join(s)


BTN_VARIANT = {"primary": "primary", "secondary": "secondary",
               "danger": "danger", "chip": "chip"}


def render(node_id, nodes, pages_index):
    n = nodes.get(node_id)
    if not n:
        return ""
    t = n.get("type")
    children = n.get("childrenIds", [])
    label = n.get("label", "")
    layout = n.get("layout", {})
    attrs = n.get("attributes", {})
    action = n.get("action")

    def kids():
        return "".join(render(c, nodes, pages_index) for c in children)

    # navigate href
    href = None
    if action and action.get("type") == "navigate":
        tgt = action.get("targetPageNodeId")
        if tgt:
            href = f"{tgt}.html"

    if t == "page":
        return kids()
    if t == "body":
        return f'<main class="wf-body">{kids()}</main>'
    if t == "row":
        return f'<div class="wf-row" style="{style_from_layout(layout)}">{kids()}</div>'
    if t == "column":
        return f'<div class="wf-col" style="{style_from_layout(layout)}">{kids()}</div>'
    if t == "text":
        cls = SIZE_CLASS.get(n.get("size", "md"), "t-md")
        return f'<div class="wf-text {cls}">{esc(label)}</div>'
    if t == "button":
        variant = BTN_VARIANT.get(n.get("variant", ""), "")
        cls = "wf-btn" + (f" {variant}" if variant else "")
        if n.get("activeIndex") is not None:
            cls += " active"
        if href:
            return f'<a class="{cls}" href="{href}">{esc(label)}</a>'
        return f'<button class="{cls}">{esc(label)}</button>'
    if t == "spacer":
        return '<div class="wf-spacer"></div>'
    if t == "image":
        round_cls = " round" if n.get("imageRound") else ""
        sz = n.get("imageSize")
        st = []
        if sz:
            st.append(f"width:{sz}px;height:{sz}px;flex:0 0 auto")
        h = layout.get("height")
        if h:
            st.append(f"height:{h}px")
        return (f'<div class="wf-image{round_cls}" style="{";".join(st)}">'
                f'<span>{esc(label)}</span></div>')
    if t == "box":
        outlined = "outlined" in attrs
        cls = "wf-box" + (" outlined" if outlined else "")
        inner = kids()
        if href:
            return f'<a class="{cls} clickable" href="{href}">{inner}</a>'
        return f'<div class="{cls}">{inner}</div>'
    if t == "input":
        it = n.get("inputType", "text")
        if it == "select":
            return f'<div class="wf-input select"><span>{esc(label or "선택")}</span><span class="caret">▾</span></div>'
        if it == "search":
            return f'<div class="wf-input search"><span>🔍 {esc(label or "검색")}</span></div>'
        if it == "area":
            return f'<div class="wf-input area"><span>{esc(label or "내용 입력")}</span></div>'
        if it == "toggle":
            on = "on" in (n.get("attributes") or {})
            state = "켜짐" if on else "꺼짐"
            return (f'<div class="wf-toggle-row"><span>{esc(label or "")}</span>'
                    f'<span class="wf-toggle {"on" if on else ""}"><span class="knob"></span>'
                    f'<span class="tg-label">{state}</span></span></div>')
        ph = label or ("비밀번호" if it == "password" else "입력")
        return f'<div class="wf-input"><span>{esc(ph)}</span></div>'
    if t == "table":
        cols = [c.strip() for c in (label or "").split(",") if c.strip()]
        rows = n.get("listRows", 3)
        thead = "".join(f"<th>{esc(c)}</th>" for c in cols)
        tr = "<tr>" + "".join('<td><span class="wf-cell"></span></td>' for _ in cols) + "</tr>"
        return (f'<table class="wf-table"><thead><tr>{thead}</tr></thead>'
                f'<tbody>{tr * rows}</tbody></table>')
    if t == "overlay":
        return f'<div class="wf-overlay"><div class="wf-overlay-inner">{kids()}</div></div>'
    # fallback
    return f'<div class="wf-unknown" data-type="{esc(t)}">{esc(label)}{kids()}</div>'


# 햄버거 드로어 목차 — 같은 주제끼리 묶음 (메인 페이지와 동일 구성)
GROUPS = [
    ("메인 · 소식", ["n2", "n3"]),
    ("크루 · 멤버", ["n7", "n8", "n9", "n10"]),
    ("아카이브", ["n15", "n16", "n17"]),
    ("클립", ["n22", "n23", "n24"]),
    ("방송 일정", ["n29", "n30", "n31"]),
    ("멀티뷰", ["n35", "n36"]),
    ("공지", ["n40", "n41", "n42"]),
    ("관리자", ["n44", "n45", "n46", "n47", "n48"]),
]

# 08 관리자 그룹 pid — 권한 보유 계정만 노출/접근
ADMIN_PIDS = {pid for title, pids in GROUPS if title == "관리자" for pid in pids}

# 관리자 권한 페이지 접근 가드 (n44~n48) — sessionStorage.soop_user 의 role 확인
ADMIN_GUARD_JS = (
    "<script>(function(){var u=null;"
    "try{u=JSON.parse(sessionStorage.getItem('soop_user')||'null');}catch(e){}"
    "if(!u||(u.role!=='admin'&&u.role!=='editor')){"
    "alert('관리자 권한이 필요한 페이지입니다.\\n메인 페이지에서 숲(SOOP) 계정으로 로그인하세요.');"
    "location.replace('../index.html');}})();</script>"
)

DRAWER_JS = (
    "<script>(function(){"
    # 숲 권한 보유 시 관리자 전용 메뉴 노출
    "var u=null;try{u=JSON.parse(sessionStorage.getItem('soop_user')||'null');}catch(e){}"
    "if(u&&(u.role==='admin'||u.role==='editor')){"
    "[].forEach.call(document.querySelectorAll('.admin-only'),function(el){el.classList.add('is-shown');});}"
    "var h=document.getElementById('wfHamb'),d=document.getElementById('wfDrawer');"
    "if(!h||!d)return;"
    "function set(o){d.classList.toggle('open',o);"
    "h.setAttribute('aria-expanded',o?'true':'false');"
    "d.setAttribute('aria-hidden',o?'false':'true');}"
    "h.addEventListener('click',function(){set(!d.classList.contains('open'));});"
    "d.addEventListener('click',function(e){if(e.target===d)set(false);});"
    "document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false);});"
    "})();</script>"
)


def page_nav(pages_index, current):
    names = dict(pages_index)
    cur_name = names.get(current, "")

    groups_html = []
    for i, (gtitle, pids) in enumerate(GROUPS, 1):
        sub_items = []
        for j, pid in enumerate(pids, 1):
            if pid not in names:
                continue
            cls = ' class="active"' if pid == current else ''
            # 메인 홈(n2)은 실제 완성 메인 페이지로 연결
            target = "../index.html" if pid == "n2" else f"{pid}.html"
            sub_items.append(
                f'<li><a{cls} href="{target}">'
                f'<span class="sn">{i}-{j}</span>{esc(names[pid])}</a></li>')
        grp_cls = "wf-grp admin-only" if gtitle == "관리자" else "wf-grp"
        groups_html.append(
            f'<li class="{grp_cls}">'
            f'<div class="wf-grp-t" tabindex="0"><span class="wf-grp-mn">{i:02d}</span>{esc(gtitle)}</div>'
            f'<ul class="wf-sub">{"".join(sub_items)}</ul>'
            '</li>')

    topbar = ('<header class="wf-topbar">'
              '<a class="wf-logo" href="../index.html">고래<span>상사</span></a>'
              f'<div class="wf-pagename">{esc(cur_name)}</div>'
              '<div class="wf-top-spacer"></div>'
              '<a class="wf-home" href="index.html">⌂ 전체 목차</a>'
              '<button class="wf-hamb" id="wfHamb" type="button" aria-label="메뉴 열기"'
              ' aria-expanded="false" aria-controls="wfDrawer">'
              '<span></span><span></span><span></span></button>'
              '</header>')

    drawer = ('<div class="wf-drawer" id="wfDrawer" aria-hidden="true">'
              '<ul class="wf-gnb">' + "".join(groups_html) + '</ul>'
              '<div class="wf-drawer-btm">'
              '<a href="../index.html">🏠 메인 페이지</a>'
              '<a href="index.html">⌂ 전체 목차</a>'
              '</div></div>')

    return topbar + drawer + DRAWER_JS


def build():
    files = sorted(glob.glob(os.path.join(DATA, "*.json")))
    pages = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        pages.append(d)
    # index order by pageNodeId numeric
    def keyf(d):
        pid = d["pageNodeId"]
        try:
            return int(pid[1:])
        except Exception:
            return 9999
    pages.sort(key=keyf)
    pages_index = [(d["pageNodeId"], d["pageName"]) for d in pages]

    for d in pages:
        pid = d["pageNodeId"]
        body = render(d["rootId"], d["nodes"], pages_index)
        guard = ADMIN_GUARD_JS if pid in ADMIN_PIDS else ""
        doc = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(d['pageName'])} · 고래상사 와이어프레임</title>
<link rel="stylesheet" href="wireframe.css">
{guard}</head><body>
{page_nav(pages_index, pid)}
<div class="wf-canvas">{body}</div>
</body></html>"""
        with open(os.path.join(OUT, f"{pid}.html"), "w", encoding="utf-8") as fh:
            fh.write(doc)

    # index page
    cards = "".join(
        f'<a class="idx-card" href="{"../index.html" if pid == "n2" else pid + ".html"}">'
        f'<span class="idx-id">{pid}</span>'
        f'<span class="idx-name">{esc(pname)}</span></a>'
        for pid, pname in pages_index)
    idx = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>고래상사 와이어프레임 — 전체 페이지</title>
<link rel="stylesheet" href="wireframe.css">
</head><body>
<div class="idx-wrap">
<h1>고래상사 공식 홈페이지 — 와이어프레임
  <a class="idx-main-link" href="../index.html">← 메인 페이지</a>
</h1>
<p class="idx-sub">manyfast 와이어프레임 v1 · 총 {len(pages_index)}개 페이지</p>
<div class="idx-grid">{cards}</div>
</div>
</body></html>"""
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(idx)
    print(f"built {len(pages_index)} pages -> {OUT}")


if __name__ == "__main__":
    build()
