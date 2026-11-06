#!/usr/bin/env python3
"""Regenerate every StaySync icon / splash asset from one design.

Run from the frontend/ folder:   python3 scripts/generate_icons.py
Needs Pillow (pip install pillow). Writes into public/ (PWA) and, when the
native projects exist, android/ and ios/. Edit the constants below to rebrand.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
C1, C2 = (99, 102, 241), (6, 182, 212)   # brand gradient: indigo -> cyan
DARK = (15, 23, 42)                       # app background #0f172a
SS = 4                                    # supersampling factor for crisp edges


def gradient(size):
    """Diagonal brand gradient square."""
    g = Image.new("RGB", (size, size))
    px = g.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = tuple(round(C1[i] + (C2[i] - C1[i]) * t) for i in range(3))
    return g


def house_mask(size, scale=1.0):
    """White house silhouette (L mask), centred on the canvas. scale<1 shrinks it."""
    m = Image.new("L", (size * SS, size * SS), 0)
    d = ImageDraw.Draw(m)
    S = size * SS

    def pt(x, y):  # house is designed in a 0..1 box centred at (0.5, 0.5)
        return (S * (0.5 + (x - 0.5) * scale), S * (0.5 + (y - 0.5) * scale))

    d.polygon([pt(0.5, 0.22), pt(0.82, 0.50), pt(0.72, 0.50), pt(0.72, 0.78),
               pt(0.28, 0.78), pt(0.28, 0.50), pt(0.18, 0.50)], fill=255)
    d.rounded_rectangle([*pt(0.45, 0.60), *pt(0.55, 0.78)], radius=S * 0.01 * scale, fill=0)  # door
    return m.resize((size, size), Image.LANCZOS)


def icon(size, scale=1.0, bg=None):
    """Full-bleed square icon: gradient (or bg colour) + white house."""
    base = gradient(size) if bg is None else Image.new("RGB", (size, size), bg)
    base.paste((255, 255, 255), (0, 0), house_mask(size, scale))
    return base


def rounded(img, radius_frac):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, *img.size], radius=img.size[0] * radius_frac, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def circle(img):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, *img.size], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def foreground(size):
    """Android adaptive-icon foreground: transparent, house inside the 66/108 safe zone."""
    fg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    fg.paste((255, 255, 255, 255), (0, 0), house_mask(size, 0.62))
    return fg


def splash(w, h):
    img = Image.new("RGB", (w, h), DARK)
    side = round(min(w, h) * 0.26)
    ic = rounded(icon(side * 2), 0.22).resize((side, side), Image.LANCZOS)
    img.paste(ic, ((w - side) // 2, (h - side) // 2), ic)
    return img


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("wrote", path.relative_to(ROOT))


# ---- PWA / web ---------------------------------------------------------------
pub = ROOT / "public"
save(icon(1024).resize((192, 192), Image.LANCZOS), pub / "pwa-192x192.png")
save(icon(1024).resize((512, 512), Image.LANCZOS), pub / "pwa-512x512.png")
save(icon(1024, 0.62).resize((512, 512), Image.LANCZOS), pub / "pwa-maskable-512x512.png")   # full-bleed, safe zone
save(icon(1024).resize((180, 180), Image.LANCZOS), pub / "apple-touch-icon.png")

# ---- iOS ---------------------------------------------------------------------
ios = ROOT / "ios/App/App/Assets.xcassets"
if ios.exists():
    save(icon(1024), ios / "AppIcon.appiconset/AppIcon-512@2x.png")   # App Store icon: square, no alpha
    for f in (ios / "Splash.imageset").glob("*.png"):
        save(splash(2732, 2732), f)

# ---- Android -----------------------------------------------------------------
res = ROOT / "android/app/src/main/res"
if res.exists():
    for dpi, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        big = icon(px * 4)
        save(rounded(big, 0.22).resize((px, px), Image.LANCZOS), res / f"mipmap-{dpi}/ic_launcher.png")
        save(circle(big).resize((px, px), Image.LANCZOS), res / f"mipmap-{dpi}/ic_launcher_round.png")
    for dpi, px in {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}.items():
        save(foreground(px * 2).resize((px, px), Image.LANCZOS), res / f"mipmap-{dpi}/ic_launcher_foreground.png")
    for f in res.glob("drawable*/splash.png"):
        w, h = Image.open(f).size
        save(splash(w, h), f)
    # gradient adaptive-icon background (vector) used instead of a flat colour
    (res / "drawable/ic_launcher_background.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    xmlns:aapt="http://schemas.android.com/aapt"\n'
        '    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">\n'
        '  <path android:pathData="M0,0h108v108h-108z">\n'
        '    <aapt:attr name="android:fillColor">\n'
        '      <gradient android:startX="0" android:startY="0" android:endX="108" android:endY="108" android:type="linear">\n'
        '        <item android:offset="0" android:color="#6366F1"/>\n'
        '        <item android:offset="1" android:color="#06B6D4"/>\n'
        '      </gradient>\n'
        '    </aapt:attr>\n'
        '  </path>\n'
        '</vector>\n')
    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        p = res / "mipmap-anydpi-v26" / name
        p.write_text(p.read_text().replace("@color/ic_launcher_background", "@drawable/ic_launcher_background"))
    print("android adaptive icon background -> gradient vector")
