#!/usr/bin/env python3
"""Build the public site from content/site.json.

  content/site.json  +  src/index.template.html
        └──► index.html   (data inlined, SEO meta filled)
        └──► feed.xml     (RSS of the `updates` list)
        └──► sitemap.xml
        └──► favicon.png / favicon.ico / apple-touch-icon.png / og-avatar.png  (all from avatar.jpg; needs Pillow)

Run:  python3 build.py            (from the site folder)
Exit code 1 = content failed validation; nothing is written.
"""
import json, re, sys, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "content" / "site.json"
TPL = ROOT / "src" / "index.template.html"

# ---------- 1. load + validate ----------
S = json.loads(SRC.read_text(encoding="utf-8"))
errors = []
for key in ("meta", "score", "verdict", "workflows", "knowledge", "routines", "outputs", "updates", "principles", "about", "footer"):
    if key not in S:
        errors.append(f"missing top-level key: {key}")
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", S["meta"].get("data_date", "")):
    errors.append("meta.data_date must be YYYY-MM-DD")
if not str(S["meta"].get("site_url", "")).endswith("/"):
    errors.append("meta.site_url must end with '/'")
for u in S["updates"]:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", u.get("date", "")):
        errors.append(f"update has bad date: {u}")
dims = S["score"]["dims"]
if dims:
    calc = round(sum(d["value"] for d in dims) / len(dims), 1)
    if abs(calc - S["score"]["overall"]) > 0.15:
        errors.append(f"score.overall {S['score']['overall']} != mean of dims {calc} (fix one or the other)")

# ---------- 1b. Chinese layer: content/site.zh.json (Simplified) merged over EN structure, converted to Traditional ----------
ZH_SRC = ROOT / "content" / "site.zh.json"
def merge(en, zh, path="root"):
    """Take text from zh where present, everything else (numbers, flags, icons, dates) from en."""
    if isinstance(en, dict):
        out = {}
        for k, v in en.items():
            out[k] = merge(v, zh.get(k), f"{path}.{k}") if isinstance(zh, dict) and k in zh else v
        return out
    if isinstance(en, list):
        if not isinstance(zh, list) or len(zh) != len(en):
            errors.append(f"zh list length mismatch at {path}: en {len(en)} vs zh {len(zh) if isinstance(zh, list) else 'missing'}")
            return en
        return [merge(a, b, f"{path}[{i}]") for i, (a, b) in enumerate(zip(en, zh))]
    if isinstance(en, str) and isinstance(zh, str):
        return zh
    return en

Z = None
if ZH_SRC.exists():
    zh_raw = json.loads(ZH_SRC.read_text(encoding="utf-8"))
    zh_raw.pop("_note", None)
    Z = merge(S, zh_raw)
    try:
        from opencc import OpenCC
        cc = OpenCC("s2twp")
        def conv(x):
            if isinstance(x, str): return cc.convert(x).replace(",", "，").replace(";", "；").replace(":", "：").replace("(", "（").replace(")", "）")
            if isinstance(x, list): return [conv(i) for i in x]
            if isinstance(x, dict): return {k: conv(v) for k, v in x.items()}
            return x
        Z = conv(Z)
        Z["meta"]["site_url"] = S["meta"]["site_url"]; Z["meta"]["avatar"] = S["meta"].get("avatar", "")
    except ImportError:
        errors.append("opencc missing: pip install opencc-python-reimplemented --break-system-packages")

# de-identification guard: words that must never appear on the public site
BANNED = [w.strip() for w in (ROOT / "content" / "banned_words.txt").read_text(encoding="utf-8").splitlines()
          if w.strip() and not w.startswith("#")] if (ROOT / "content" / "banned_words.txt").exists() else []
blob = json.dumps({"en": S, "zh": Z}, ensure_ascii=False).lower()
for w in BANNED:
    if w.lower() in blob:
        errors.append(f"banned word found in content: {w!r}")

if errors:
    print("BUILD FAILED — content/site.json:")
    for e in errors:
        print("  ✗", e)
    sys.exit(1)

# ---------- 2. index.html ----------
url = S["meta"]["site_url"]
title = f'{S["meta"]["name"]} — {S["meta"]["tagline"]}'
desc = S["meta"]["lede"]
data = json.dumps({"en": S, "zh": Z or S}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = (TPL.read_text(encoding="utf-8")
        .replace("{{TITLE}}", html.escape(title, quote=True))
        .replace("{{DESC}}", html.escape(desc, quote=True))
        .replace("{{URL}}", html.escape(url, quote=True))
        .replace("{{DATA}}", data))
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("✓ index.html", len(page), "bytes")

# ---------- 3. feed.xml ----------
def rfc822(d):
    return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 08:00:00 +0000")
items = sorted(S["updates"], key=lambda u: u["date"], reverse=True)
feed = ['<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        f'<title>{html.escape(title)} — updates</title>',
        f'<link>{html.escape(url)}</link>',
        f'<description>{html.escape(desc)}</description>',
        f'<lastBuildDate>{rfc822(items[0]["date"]) if items else rfc822(S["meta"]["data_date"])}</lastBuildDate>']
for u in items:
    feed += ['<item>',
             f'<title>{html.escape(u["title"])}</title>',
             f'<link>{html.escape(url)}#updates</link>',
             f'<guid isPermaLink="false">{u["date"]}-{re.sub(r"[^a-z0-9]+", "-", u["title"].lower())[:40]}</guid>',
             f'<pubDate>{rfc822(u["date"])}</pubDate>',
             f'<description>{html.escape(u.get("note", ""))}</description>',
             '</item>']
feed += ['</channel></rss>']
(ROOT / "feed.xml").write_text("\n".join(feed), encoding="utf-8")
print("✓ feed.xml", len(items), "items")

# ---------- 4. sitemap.xml ----------
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    f'<url><loc>{html.escape(url)}</loc><lastmod>{S["meta"]["data_date"]}</lastmod><changefreq>monthly</changefreq></url></urlset>\n',
    encoding="utf-8")
print("✓ sitemap.xml")

# ---------- 5. icons + social image, all derived from avatar.jpg ----------
try:
    from PIL import Image
    av = ROOT / (S["meta"].get("avatar") or "avatar.jpg")
    im = Image.open(av).convert("RGB")
    side = min(im.size); im = im.crop(((im.width-side)//2, (im.height-side)//2, (im.width+side)//2, (im.height+side)//2))
    im.resize((500, 500), Image.LANCZOS).save(ROOT / "og-avatar.png")          # social preview (square card)
    im.resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png")   # iOS home screen
    im.resize((64, 64), Image.LANCZOS).save(ROOT / "favicon.png")              # browser tab
    im.resize((64, 64), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64)])
    print("✓ og-avatar.png · apple-touch-icon.png · favicon.png · favicon.ico (from", av.name + ")")
except ImportError:
    print("· icons skipped (pip install pillow to enable)")

print("done —", S["meta"]["data_date"], "·", len(S["workflows"]), "workflows ·", len(S["updates"]), "updates")
