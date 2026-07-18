# §2.6-6: 그룹별 og:image 생성 — 기존 og.png 스타일(다크+블루/틸 글로우+아웃라인 워터마크) 재현
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = "/mnt/c/Users/kyefy/OneDrive/바탕 화면/개인자료/03_WCHP/고래상사 리워크"
BOLD = "/mnt/c/Windows/Fonts/malgunbd.ttf"
W, H = 1200, 630

VARIANTS = {
    "crew":      ("CREW & MEMBERS",     "크루",   " & 멤버",   "16인의 프로필과 부서, 라이브 상태를 한곳에서"),
    "archive":   ("CONTENT ARCHIVE",    "콘텐츠", " 아카이브", "크루대전과 컨텐츠 기록, 성적 통계까지"),
    "clips":     ("BEST CLIPS",         "베스트", " 클립",     "다시 보고 싶은 명장면 모음"),
    "schedule":  ("BROADCAST SCHEDULE", "방송",   " 일정",     "이번 주 방송을 캘린더로 확인하세요"),
    "multiview": ("MULTIVIEW",          "멀티뷰", " 시청",     "동시 방송을 한 화면에서"),
    "notice":    ("NEWS & NOTICE",      "소식",   "·공지",     "고래상사의 새로운 소식"),
}

TEAL = (34, 197, 176)
INK2 = (156, 170, 198)


def base_bg():
    # 저해상도 픽셀 계산 → 리사이즈로 부드러운 그라데이션 (블루=좌하, 틸=우상)
    sw, sh = 60, 32
    im = Image.new("RGB", (sw, sh))
    px = im.load()
    for y in range(sh):
        for x in range(sw):
            nx, ny = x / sw, y / sh
            d_blue = ((nx) ** 2 + (1 - ny) ** 2) ** 0.5      # 좌하 거리
            d_teal = ((1 - nx) ** 2 + (ny) ** 2) ** 0.5      # 우상 거리
            fb = max(0.0, 1 - d_blue / 0.75) ** 1.6
            ft = max(0.0, 1 - d_teal / 0.8) ** 2.0
            r = 7 + int(25 * fb) + int(0 * ft)
            g = 10 + int(45 * fb) + int(55 * ft)
            b = 20 + int(160 * fb) + int(50 * ft)
            px[x, y] = (min(r, 255), min(g, 255), min(b, 255))
    return im.resize((W, H), Image.BICUBIC)


def make(slug, en, t_white, t_teal, sub):
    img = base_bg().convert("RGBA")
    d = ImageDraw.Draw(img)

    # 아웃라인 워터마크 (WHALE CORP)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    f_wm = ImageFont.truetype(BOLD, 118)
    dw.text((40, 55), "WHALE CORP", font=f_wm, fill=(255, 255, 255, 0),
            stroke_width=2, stroke_fill=(255, 255, 255, 26))
    img = Image.alpha_composite(img, wm)
    d = ImageDraw.Draw(img)

    f_eye = ImageFont.truetype(BOLD, 30)
    f_big = ImageFont.truetype(BOLD, 128)
    f_sub = ImageFont.truetype(BOLD, 36)

    d.text((60, 250), "WHALE-CORP  " + en, font=f_eye, fill=TEAL)
    x = 55
    d.text((x, 305), t_white, font=f_big, fill=(238, 242, 251))
    w1 = d.textlength(t_white, font=f_big)
    d.text((x + w1, 305), t_teal, font=f_big, fill=TEAL)
    d.text((60, 485), sub, font=f_sub, fill=INK2)

    out = img.convert("RGB").quantize(colors=224, dither=Image.FLOYDSTEINBERG).convert("RGB")
    path = os.path.join(OUT, f"og-{slug}.png")
    out.save(path, optimize=True)
    return path, os.path.getsize(path)


total = 0
for slug, (en, tw, tt, sub) in VARIANTS.items():
    p, s = make(slug, en, tw, tt, sub)
    total += s
    print(f"{os.path.basename(p)}: {s//1024}KB")
print(f"총량: {total//1024}KB")
