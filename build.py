#!/usr/bin/env python3
"""Doc content.json roi sinh ra index.html (mot file tu chua, khong CDN).

Ba nhom layout, khong hon:
  split  1 the lon "doc truoc" + cac the con      (chi nhom dau)
  grid   luoi the doc dong nhat, co the kem tab loc (moi nhom giua)
  dark   dai mau dam: kenh ho tro + danh sach doc  (chi nhom cuoi)
Danh tinh moi nhom nam o header + nen tint, khong o kieu bo cuc.
"""
import base64
import json
import html
import pathlib
import urllib.parse

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
meta = data["meta"]

# Newest first within each group / subgroup, by wiki node creation date.
for _g in data["groups"]:
    if _g.get("keep_order"):
        continue
    for _docs in ([sg["docs"] for sg in _g["subgroups"]] if "subgroups" in _g else [_g["docs"]]):
        _docs.sort(key=lambda d: d.get("created", ""), reverse=True)
WIKI = meta["wiki_base"]

_FAV = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
    "<rect width='32' height='32' rx='7' fill='#3370ff'/>"
    "<g fill='#ffffff'>"
    "<rect x='9' y='10' width='14' height='2.6' rx='1.3'/>"
    "<rect x='9' y='14.7' width='14' height='2.6' rx='1.3'/>"
    "<rect x='9' y='19.4' width='9' height='2.6' rx='1.3'/>"
    "</g></svg>"
)
FAVICON = "data:image/svg+xml," + urllib.parse.quote(_FAV)


def _png(name):
    return "data:image/png;base64," + base64.b64encode((HERE / "assets" / name).read_bytes()).decode()


# Lark logo as the page cursor. A static CSS cursor is the fallback (no JS, touch);
# with a fine pointer, JS swaps it for #lc, an animated logo that follows the mouse:
# grows in, shrinks to half and spins fast while over a doc card.
KV = "data:image/jpeg;base64," + base64.b64encode((HERE / "assets" / "lark-kv-3d.jpg").read_bytes()).decode()
LOGO = _png("lark-logo.png")
CUR1, CUR2, CUR_BIG = _png("hand-32.png"), _png("hand-64.png"), _png("hand-64.png")
CURSOR_CSS = f"""html, body, a, button, [role=tab] {{ cursor: url({CUR1}) 9 1, auto;
  cursor: image-set(url({CUR1}) 1x, url({CUR2}) 2x) 9 1, auto; }}
html.lc-on, html.lc-on * {{ cursor: none !important; }}
#lc {{ position: fixed; left: 0; top: 0; width: 32px; height: 30px; margin: -1px 0 0 -9px;
  pointer-events: none; z-index: 2147483647; opacity: 0; transition: opacity .2s; }}
#lc.on {{ opacity: 1; }}
#lc i {{ display: block; width: 100%; height: 100%; transform: scale(0);
  transition: transform .3s cubic-bezier(.34, 1.56, .64, 1); }}
#lc.on i {{ transform: scale(1); }}
#lc.on.hot i {{ transform: scale(1.18) rotate(-10deg); transform-origin: 9px 1px; }}
#lc b {{ display: block; width: 100%; height: 100%; background: url({CUR_BIG}) center / contain no-repeat; }}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def docs_of(group):
    if "subgroups" in group:
        return [d for sg in group["subgroups"] for d in sg["docs"]]
    return group["docs"]


total_docs = sum(len(docs_of(g)) for g in data["groups"])
LOCK_NOTE = (
    "Thẻ gắn nhãn <b>Cần quyền truy cập</b> hiện chưa mở chia sẻ ra ngoài tổ chức, "
    "vui lòng liên hệ người phụ trách. "
    if any(not d["shared"] for g in data["groups"] for d in docs_of(g))
    else ""
)

LEVEL = {"Cơ bản": "lv1", "Trung cấp": "lv2", "Nâng cao": "lv3"}


def attrs(doc):
    """Thuoc tinh chung cho moi phan tu tai lieu, dung cho tab loc chu de."""
    return (
        f'href="{WIKI}{esc(doc["token"])}" target="_blank" rel="noopener" '
        f'data-topics="{esc(" ".join(doc.get("topics", [])))}"'
    )


def meta_row(doc):
    bits = [
        f'<span class="badge {LEVEL.get(doc["level"], "lv1")}">{esc(doc["level"])}</span>',
        f'<span class="badge lang">{esc(doc["lang"])}</span>',
    ]
    if not doc["shared"]:
        bits.append('<span class="badge lock">Cần quyền truy cập</span>')
    return "".join(bits)


# --------------------------------------------------------------- the doc card
def card(d, sg=None):
    sgattr = f' data-sg="{esc(sg)}"' if sg else ""
    return f"""          <a class="card item"{sgattr} {attrs(d)}>
            <div class="badges">{meta_row(d)}</div>
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
            <div class="card-foot"><span class="time">{d['minutes']} phút đọc</span><span class="go">Mở tài liệu →</span></div>
          </a>
"""


# ----------------------------------------------------------------- templates
def t_split(g):
    lead, *rest = g["docs"]
    side = "".join(card(d) for d in rest)
    return f"""      <div class="split">
        <a class="feature item" {attrs(lead)}>
          <h3>{esc(lead['title'])}</h3>
          <p>{esc(lead['desc'])}</p>
          <div class="feature-foot">
            <div class="badges">{meta_row(lead)}</div>
            <span class="time">{lead['minutes']} phút đọc</span>
          </div>
          <span class="btn">Mở tài liệu →</span>
        </a>
        <div class="split-side">
{side}        </div>
      </div>
"""


def t_grid(g):
    if "subgroups" in g:
        tabs = '<button type="button" class="tab on" data-tab="all">Tất cả</button>'
        cards = ""
        for i, sg in enumerate(g["subgroups"]):
            key = f"sg{i}"
            tabs += (
                f'<button type="button" class="tab" data-tab="{key}">'
                f'{esc(sg["name"])}</button>'
            )
            cards += "".join(card(d, sg=key) for d in sg["docs"])
            if not sg["docs"]:
                cards += (
                    f'          <div class="card item soon" data-sg="{key}" data-topics="ai">'
                    '<div class="badges"><span class="badge lang">Sắp có</span></div>'
                    f'<h3>{esc(sg["name"])}</h3><p>Tài liệu đang được bổ sung.</p></div>\n'
                )
        return f'      <div class="tabs">{tabs}</div>\n      <div class="grid">\n{cards}      </div>\n'
    body = "".join(card(d) for d in g["docs"])
    return f'      <div class="grid">\n{body}      </div>\n'


def t_dark(g):
    chans = "".join(
        f"""          <div class="chan">
            <span class="chan-n">{i}</span>
            <b>{esc(c['name'])}</b><span>{esc(c['desc'])}</span>
          </div>
"""
        for i, c in enumerate(g["channels"], 1)
    )
    links = "".join(
        f"""          <a class="dlink item" {attrs(d)}>
            <span class="dlink-t">{esc(d['title'])}</span>
            <span class="dlink-d">{esc(d['desc'])}</span>
            <span class="arrow">→</span>
          </a>
"""
        for d in g["docs"]
    )
    return f"""      <div class="dark-grid">
        <div class="chans">
{chans}        </div>
        <div class="dlinks">
          <h3 class="dsub">Tài liệu kèm theo</h3>
{links}        </div>
      </div>
"""


TEMPLATES = {"split": t_split, "grid": t_grid, "dark": t_dark}

# ------------------------------------------------------------------ assemble
navs, sections = [], []
# Muc lon tren thanh dieu huong: gom cac nhom theo thu tu Tinh nang, Lark x AI, Quan tri, Kiem tra ky thuat.
CLUSTERS = [
    ("Tính năng của Lark", ["gia-tri", "bat-dau", "quy-trinh", "base"]),
    ("Lark x AI", ["ai"]),
    ("Quản trị và bảo mật", ["quan-tri"]),
    ("Kiểm tra kỹ thuật", ["ho-tro"]),
]
RENAME = {"ai": "Lark x AI", "ho-tro": "Kiểm tra kỹ thuật"}
_present = {g["id"] for g in data["groups"]}
for label, ids in CLUSTERS:
    ids = [i for i in ids if i in _present]
    if ids:
        navs.append(
            f'<a class="nav-item" href="#{ids[0]}" data-nav="{ids[0]}" data-ids="{" ".join(ids)}">{esc(label)}</a>'
        )
for g in data["groups"]:
    cls = " ".join(
        filter(
            None,
            [
                "section",
                "tint" if g.get("tint") else "",
                "dark" if g["template"] == "dark" else "",
            ],
        )
    )
    sections.append(
        f"""  <section class="{cls}" id="{esc(g['id'])}">
    <div class="wrap">
      <div class="sec-head">
        <h2>{esc(RENAME.get(g['id'], g['name']))}</h2>
        <p class="lead">{esc(g['lead'])}</p>
      </div>
{TEMPLATES[g['template']](g)}    </div>
  </section>
"""
    )

all_docs = [d for g in data["groups"] for d in docs_of(g)]
topic_tabs = "".join(
    f'<button type="button" class="topic" data-topic="{esc(t["id"])}" aria-pressed="false">'
    f'{esc(t["label"])}<span>{sum(t["id"] in d.get("topics", []) for d in all_docs)}</span></button>'
    for t in data["topics"]
)

HTML = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<meta name="description" content="{esc(meta['subtitle'])}">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['subtitle'])}">
<meta property="og:type" content="website">
<link rel="icon" href="{FAVICON}">
<title>{esc(meta['title'])}</title>
<style>
:root {{
  --bg: #ffffff;
  --tint: #f3f6fc;
  --ink: #01143e;
  --text: #10162b;
  --muted: #5b6273;
  --line: #e6e9f0;
  --line-soft: #eef1f7;
  --brand: #3370ff;
  --brand-dk: #1d54e0;
  --brand-soft: #eaf0ff;
  --warn: #b5271f;
  --warn-soft: #fdeceb;
  --r-sm: 8px;
  --r-md: 14px;
  --r-full: 999px;
}}
* {{ box-sizing: border-box; margin: 0; }}
html {{ scroll-behavior: smooth; background: var(--bg); }}
{CURSOR_CSS}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", Roboto, Helvetica, Arial, sans-serif;
  font-size: 15px; line-height: 1.62; -webkit-font-smoothing: antialiased;
}}
a {{ color: inherit; text-decoration: none; }}
.wrap {{ max-width: 1140px; margin: 0 auto; padding: 0 24px; }}

:focus-visible {{ outline: 2px solid var(--brand); outline-offset: 2px; border-radius: var(--r-sm); }}
.section.dark :focus-visible {{ outline-color: #7ea3ff; }}

/* ============ header ============ */
header {{
  position: sticky; top: 0; z-index: 30; background: rgba(255,255,255,.92);
  backdrop-filter: saturate(180%) blur(12px); border-bottom: 1px solid var(--line);
}}
.head-in {{ display: flex; align-items: center; gap: 28px; height: 62px; }}
.logo {{ font-size: 16px; font-weight: 700; letter-spacing: -.02em; white-space: nowrap; }}
.logo b {{ color: var(--brand); }}
nav {{ display: flex; gap: 22px; overflow-x: auto; flex: 1; scrollbar-width: none; }}
nav::-webkit-scrollbar {{ display: none; }}
.nav-item {{
  position: relative; font-size: 13.5px; font-weight: 500; color: var(--muted);
  white-space: nowrap; padding: 20px 0; transition: color .2s;
}}
.nav-item::before {{
  content: ""; position: absolute; right: 0; bottom: 16px; width: 0; height: 2px;
  background: var(--brand); transition: width .35s ease;
}}
.nav-item:hover {{ color: var(--text); }}
.nav-item:hover::before, .nav-item.on::before {{ width: 100%; left: 0; }}
.nav-item.on {{ color: var(--brand); font-weight: 600; }}

/* ============ hero (huong A: Sky Studio) ============ */
.hero-band {{
  background: radial-gradient(900px 520px at 85% -8%, #8fc6ff 0, transparent 62%),
    linear-gradient(180deg, #d4e8ff, #f3f8ff 78%, #fff);
  overflow: hidden;
}}
.hero {{ padding: 64px 0 46px; }}
.hero-grid {{ display: grid; grid-template-columns: .95fr 1.25fr; gap: 40px; align-items: center; perspective: 1500px; }}
.eyebrow {{
  display: inline-block; padding: 6px 14px; border-radius: var(--r-full); background: #fff;
  font-size: 13px; font-weight: 600; color: var(--brand); box-shadow: 0 6px 16px -8px rgba(30,70,190,.4);
}}
.hero h1 {{ font-size: 58px; line-height: 1; letter-spacing: -.035em; font-weight: 800; margin: 18px 0 16px; }}
.hero h1 em {{
  font-style: normal; background: linear-gradient(90deg, var(--brand), #19c3b0);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}}
.hero p {{ font-size: 16px; color: #3f4f78; max-width: 46ch; }}
.hero-cta {{ display: flex; gap: 18px; align-items: center; margin-top: 26px; font-size: 14px; color: #3f4f78; }}
.cta {{
  display: inline-flex; padding: 12px 22px; border-radius: var(--r-full); background: var(--brand); color: #fff;
  font-weight: 600; font-size: 15px; box-shadow: 0 10px 0 -4px #1f4fc9, 0 18px 28px -10px rgba(36,84,220,.55);
  transition: transform .15s, box-shadow .15s;
}}
.cta:hover {{ transform: translateY(-2px); }}
.cta:active {{ transform: translateY(4px); box-shadow: 0 4px 0 -4px #1f4fc9; }}
.kvwrap {{
  position: relative; transform-style: preserve-3d;
  transform: rotateY(calc(-9deg + var(--ry, 0deg))) rotateX(calc(3deg + var(--rx, 0deg)));
  transition: transform .18s ease-out;
}}
.kv {{
  border-radius: 36px; overflow: hidden; aspect-ratio: 4/3;
  box-shadow: 0 50px 70px -30px rgba(25,60,170,.6), 0 0 0 8px rgba(255,255,255,.65);
}}
.kv img {{ width: 100%; height: 100%; object-fit: cover; display: block; transform: scale(1.12); transform-origin: 30% 20%; }}
.chip {{
  position: absolute; display: flex; align-items: center; gap: 10px; padding: 10px 16px; border-radius: 20px;
  background: rgba(255,255,255,.84); backdrop-filter: blur(10px); font-weight: 600; font-size: 14px;
  box-shadow: 0 22px 34px -14px rgba(20,50,150,.5); color: var(--ink);
}}
.chip img {{ width: 30px; height: 24px; object-fit: contain; }}
.c1 {{ left: -34px; top: 36px; transform: translateZ(90px); }}
.dot {{ width: 10px; height: 10px; border-radius: 50%; background: #ff7a3d; }}
.dot.t {{ background: #19c3b0; }}
.topics {{
  display: inline-flex; gap: 8px; flex-wrap: wrap; margin-top: 44px; padding: 6px;
  border-radius: var(--r-full); background: rgba(255,255,255,.75);
}}
.topic {{
  -webkit-appearance: none; appearance: none; display: inline-flex; align-items: center; gap: 10px;
  padding: 10px 18px; font: inherit; font-size: 14px; font-weight: 600; color: #3f4f78;
  background: transparent; border: 0; border-radius: var(--r-full);
  transition: color .18s, background .18s, box-shadow .18s;
}}
.topic span {{
  min-width: 24px; padding: 1px 7px; font-size: 12px; font-weight: 600; text-align: center;
  color: var(--brand-dk); background: var(--brand-soft); border-radius: var(--r-full);
}}
.topic:hover {{ color: var(--brand); }}
.topic.on {{ background: var(--brand); color: #fff; box-shadow: 0 8px 14px -6px rgba(40,90,230,.6); }}
.topic.on span {{ background: rgba(255,255,255,.22); color: #fff; }}

/* ============ section shell ============ */
.section {{ padding: 74px 0; scroll-margin-top: 62px; }}
.section.tint {{ background: var(--tint); }}
.sec-head {{ margin-bottom: 34px; max-width: 70ch; }}
.sec-head h2 {{
  font-size: 27px; font-weight: 700; letter-spacing: -.025em; position: relative;
  display: inline-block; padding-bottom: 9px;
}}
.sec-head h2::before {{
  content: ""; position: absolute; left: 0; right: 42%; bottom: 0; height: 2px; background: var(--brand);
}}
.lead {{ margin-top: 10px; font-size: 14.5px; color: var(--muted); }}

/* shared bits */
.badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.badge {{ font-size: 10.5px; font-weight: 600; padding: 3px 8px; border-radius: var(--r-sm); white-space: nowrap; }}
.lv1 {{ background: var(--brand-soft); color: var(--brand-dk); }}
.lv2 {{ background: #d6e4ff; color: #1a49c4; }}
.lv3 {{ background: var(--brand-dk); color: #fff; }}
.lang {{ background: #eef1f7; color: var(--muted); }}
.lock {{ background: var(--warn-soft); color: var(--warn); }}
.time {{ font-size: 12px; color: var(--muted); white-space: nowrap; }}
.go {{ font-size: 12.5px; font-weight: 600; color: var(--brand); }}
.arrow {{ color: var(--muted); font-size: 17px; transition: transform .2s, color .2s; }}

/* ============ split (nhom dau) ============ */
.split {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; align-items: stretch; }}
.feature {{
  display: flex; flex-direction: column; gap: 12px; padding: 34px 34px 30px;
  background: var(--ink); border-radius: var(--r-md); color: #fff;
  transition: transform .22s;
}}
.feature:hover {{ transform: translateY(-3px); }}
.feature h3 {{ font-size: 25px; line-height: 1.25; letter-spacing: -.02em; }}
.feature p {{ font-size: 14px; color: #c2ccdf; line-height: 1.65; flex: 1; }}
.feature-foot {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
.feature .badge {{ background: rgba(255,255,255,.16); color: #e4ebfa; }}
.feature .lv3 {{ background: #4a80ff; color: #fff; }}
.feature .lock {{ background: rgba(255,150,144,.22); color: #ffc0bc; }}
.feature .time {{ color: #9aa6bf; }}
.btn {{
  align-self: flex-start; margin-top: 6px; padding: 10px 20px; border-radius: var(--r-sm);
  background: var(--brand); color: #fff; font-size: 13px; font-weight: 600;
  transition: background .2s;
}}
.feature:hover .btn {{ background: #4a80ff; }}
.split-side {{ display: flex; flex-direction: column; gap: 16px; }}

/* ============ grid (cac nhom giua) ============ */
.tabs {{ display: flex; flex-wrap: wrap; gap: 6px 22px; margin-bottom: 22px; }}
.tab {{
  -webkit-appearance: none; appearance: none; background: none; border: none; font: inherit;
  padding: 0 0 5px; font-size: 13.5px; font-weight: 600; color: var(--muted);
  border-bottom: 2px solid transparent; transition: color .2s, border-color .2s;
}}
.tab:hover {{ color: var(--text); }}
.tab.on {{ color: var(--brand); border-bottom-color: var(--brand); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(258px, 1fr)); gap: 22px; perspective: 1100px; }}
.card {{
  display: flex; flex-direction: column; gap: 9px; padding: 22px 22px 17px; background: #fff;
  border: 1px solid rgba(255,255,255,.9); border-radius: 28px; position: relative; overflow: hidden;
  box-shadow: 0 26px 36px -22px rgba(25,60,170,.45), 0 0 0 1px var(--line-soft);
  transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  transition: transform .16s ease-out, box-shadow .2s;
}}
.card::after {{
  content: ""; position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity .2s;
  background: radial-gradient(240px circle at var(--mx, 50%) var(--my, 0%), rgba(51,112,255,.14), transparent 60%);
}}
.card:hover {{
  transform: translateY(-8px) scale(1.02) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  box-shadow: 0 40px 50px -24px rgba(25,60,170,.6), 0 0 0 1px #d3ddf5;
}}
.card:hover::after {{ opacity: 1; }}
.card h3 {{ font-size: 16px; letter-spacing: -.015em; line-height: 1.35; }}
.card p {{
  font-size: 13.5px; color: var(--muted); flex: 1;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
}}
.card-foot {{ display: flex; justify-content: space-between; align-items: center; padding-top: 11px; border-top: 1px solid var(--line-soft); }}
.card .go {{ opacity: 0; transform: translateX(-4px); transition: opacity .2s, transform .2s; }}
.card:hover .go {{ opacity: 1; transform: none; }}

/* ============ dark band (nhom cuoi) ============ */
.section.dark {{ background: var(--ink); color: #fff; }}
.section.dark .lead {{ color: #aeb9cf; }}
.section.dark h2::before {{ background: #7ea3ff; }}
.dark-grid {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 44px; }}
.chans {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-content: start; }}
.chan {{
  padding: 18px 18px 16px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.1);
  border-radius: var(--r-md);
}}
.chan-n {{
  display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px;
  border-radius: var(--r-full); background: rgba(126,163,255,.2); color: #a9c2ff; font-size: 11.5px; font-weight: 700;
  margin-bottom: 8px;
}}
.chan b {{ display: block; font-size: 14.5px; margin: 0 0 5px; }}
.chan span {{ font-size: 12.5px; color: #aeb9cf; line-height: 1.55; }}
.dsub {{ font-size: 12.5px; font-weight: 600; color: #9db2d8; margin-bottom: 12px; }}
.dlink {{
  display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 10px;
  padding: 13px 0; border-bottom: 1px solid rgba(255,255,255,.1); transition: transform .2s;
}}
.dlink:hover {{ transform: translateX(6px); }}
.dlink-t {{ grid-column: 1; grid-row: 1; font-size: 14.5px; font-weight: 600; }}
.dlink-d {{
  grid-column: 1; grid-row: 2; font-size: 12.5px; color: #aeb9cf; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.dlink .arrow {{ grid-column: 2; grid-row: 1 / 3; align-self: center; color: #8ea0c0; }}
.dlink:hover .arrow {{ color: #fff; }}

/* ============ footer ============ */
footer {{ background: #000c26; color: #97a1b8; padding: 34px 0; font-size: 12.5px; line-height: 1.75; }}
footer b {{ color: #cbd3e2; }}
.empty {{ display: none; padding: 70px 0; text-align: center; color: var(--muted); font-size: 14.5px; }}
.hide {{ display: none !important; }}

/* ============ responsive ============ */
@media (max-width: 900px) {{
  .hero {{ padding: 40px 0 32px; }}
  .hero-grid {{ grid-template-columns: 1fr; gap: 44px; }}
  .hero h1 {{ font-size: 38px; }}
  .kvwrap {{ transform: none; }}
  .c1 {{ left: -8px; }}
  .split, .dark-grid {{ grid-template-columns: 1fr; }}
  .section {{ padding: 54px 0; }}
}}
@media (max-width: 600px) {{
  .wrap {{ padding: 0 16px; }}
  .head-in {{ gap: 16px; }}
  .topic {{ padding: 10px 16px; font-size: 13.5px; }}
  .grid {{ grid-template-columns: 1fr; }}
  .chans {{ grid-template-columns: 1fr; }}
  .feature {{ padding: 26px 22px 24px; }}
  .feature h3 {{ font-size: 21px; }}
  .card .go {{ opacity: 1; transform: none; }}
}}

@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  *, *::before, *::after {{
    transition-duration: .001ms !important;
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
  }}
}}
</style>
</head>
<body>

<header>
  <div class="wrap head-in">
    <span class="logo">Thư viện <b>Lark</b></span>
    <nav>{''.join(navs)}</nav>
  </div>
</header>

<div class="hero-band">
<div class="wrap hero">
  <div class="hero-grid" id="hero">
    <div>
      <span class="eyebrow">Dành cho partner và khách hàng tại Việt Nam</span>
      <h1>Thư viện Lark <em>tiếng Việt</em></h1>
      <p>{esc(meta['subtitle'])}</p>
      <div class="hero-cta"><a class="cta" href="#{esc(data['groups'][0]['id'])}">Khám phá tài liệu</a></div>
    </div>
    <div class="kvwrap" id="kvwrap" aria-hidden="true">
      <div class="kv"><img src="{KV}" alt=""></div>
      <div class="chip c1"><img src="{LOGO}" alt="">Lark</div>
    </div>
  </div>
  <div class="topics" role="group" aria-label="Lọc theo chủ đề">{topic_tabs}</div>
</div>
</div>

{''.join(sections)}
<div class="wrap"><div class="empty" id="empty">Không có tài liệu nào thuộc chủ đề này.</div></div>

<footer>
  <div class="wrap">
    {esc(meta['credit'])}.<br>
    Nội dung chi tiết nằm trong tài liệu gốc trên Lark, trang này chỉ là mục lục.{('<br>' + LOCK_NOTE) if LOCK_NOTE else ''}
  </div>
</footer>

<script>
(function () {{
  var topics = [].slice.call(document.querySelectorAll('.topic'));
  var subtabs = [].slice.call(document.querySelectorAll('.tabs'));
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  var items = [].slice.call(document.querySelectorAll('.item'));
  var sections = [].slice.call(document.querySelectorAll('.section'));
  var navs = [].slice.call(document.querySelectorAll('.nav-item'));
  var empty = document.getElementById('empty');
  var topic = null, tab = 'all';

  function apply() {{
    var shown = 0;
    items.forEach(function (el) {{
      var okT = !topic || el.dataset.topics.split(' ').indexOf(topic) > -1;
      var okG = topic || !el.dataset.sg || tab === 'all' || el.dataset.sg === tab;
      var on = okT && okG;
      el.classList.toggle('hide', !on);
      if (on) shown++;
    }});
    subtabs.forEach(function (t) {{ t.classList.toggle('hide', !!topic); }});
    sections.forEach(function (s) {{
      s.classList.toggle('hide', s.querySelectorAll('.item:not(.hide)').length === 0);
    }});
    navs.forEach(function (n) {{
      var all = n.dataset.ids.split(' ').every(function (id) {{
        var sec = document.getElementById(id);
        return !sec || sec.classList.contains('hide');
      }});
      n.classList.toggle('hide', all);
    }});
    if (window.ringBuild) window.ringBuild(topic);
    empty.style.display = shown === 0 ? 'block' : 'none';
  }}

  // Topic tabs toggle: click the active one again to show everything.
  topics.forEach(function (b) {{
    b.addEventListener('click', function () {{
      topic = topic === b.dataset.topic ? null : b.dataset.topic;
      topics.forEach(function (o) {{
        var on = o.dataset.topic === topic;
        o.classList.toggle('on', on); o.setAttribute('aria-pressed', on);
      }});
      apply();
    }});
  }});
  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{
      tab = t.dataset.tab;
      tabs.forEach(function (o) {{ o.classList.toggle('on', o === t); }});
      apply();
    }});
  }});

  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return;
      navs.forEach(function (n) {{ n.classList.toggle('on', n.dataset.ids.split(' ').indexOf(e.target.id) > -1); }});
    }});
  }}, {{ rootMargin: '-20% 0px -70% 0px' }});
  sections.forEach(function (s) {{ io.observe(s); }});
}})();
(function () {{
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var hero = document.getElementById('hero'), kv = document.getElementById('kvwrap');
  hero.addEventListener('pointermove', function (e) {{
    var r = hero.getBoundingClientRect();
    kv.style.setProperty('--ry', (((e.clientX - r.left) / r.width - .5) * 14).toFixed(2) + 'deg');
    kv.style.setProperty('--rx', (-((e.clientY - r.top) / r.height - .5) * 10).toFixed(2) + 'deg');
  }});
  hero.addEventListener('pointerleave', function () {{ kv.style.setProperty('--ry', '0deg'); kv.style.setProperty('--rx', '0deg'); }});
  document.addEventListener('pointermove', function (e) {{
    var el = e.target.closest && e.target.closest('.card'); if (!el) return;
    var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
    el.style.setProperty('--rx', (-y * 12).toFixed(2) + 'deg'); el.style.setProperty('--ry', (x * 12).toFixed(2) + 'deg');
    el.style.setProperty('--mx', ((x + .5) * 100).toFixed(1) + '%'); el.style.setProperty('--my', ((y + .5) * 100).toFixed(1) + '%');
  }}, {{ passive: true }});
  document.addEventListener('pointerout', function (e) {{
    var el = e.target.closest && e.target.closest('.card');
    if (el && !el.contains(e.relatedTarget)) {{ el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg'); }}
  }});
}})();
(function () {{
  if (!matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var c =document.createElement('div');
  c.id = 'lc'; c.setAttribute('aria-hidden', 'true'); c.innerHTML = '<i><b></b></i>';
  document.body.appendChild(c);
  document.documentElement.classList.add('lc-on');
  var x = 0, y = 0, raf = 0;
  function draw() {{ raf = 0; c.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)'; }}
  addEventListener('pointermove', function (e) {{
    x = e.clientX; y = e.clientY;
    if (!c.classList.contains('on')) {{ draw(); c.classList.add('on'); }}
    else if (!raf) raf = requestAnimationFrame(draw);
    c.classList.toggle('hot', !!(e.target.closest && e.target.closest('a.item')));
  }}, {{ passive: true }});
  document.addEventListener('mouseleave', function () {{ c.classList.remove('on', 'hot'); }});
  addEventListener('blur', function () {{ c.classList.remove('on', 'hot'); }});
}})();
</script>
</body>
</html>
"""

# Huong D (Ring Shelf): hero xanh + vong xoay 3D o tren, cac nhom bai van nam ben duoi. Day la thiet ke chinh thuc.
D_CSS = """
.hero-band { background: radial-gradient(800px 500px at 20% 0, #4d82f5, transparent 65%), linear-gradient(180deg, #2c5fe0, #2756d6); color: #fff; }
.hero h1 { color: #fff; } .hero h1 em { background: none; color: #ffd7bd; -webkit-text-fill-color: #ffd7bd; }
.hero p, .hero-cta { color: #dbe5ff; }
.eyebrow { background: rgba(255,255,255,.18); color: #fff; box-shadow: none; }
.cta { background: #ff8a4c; color: #2a1608; box-shadow: 0 7px 0 #c25a21, 0 16px 24px -8px rgba(0,0,0,.4); }
.cta:active { box-shadow: 0 2px 0 #c25a21; }
.kv { box-shadow: 0 0 0 8px rgba(255,255,255,.22), 0 40px 50px -26px rgba(0,10,80,.7); }
.chip { color: #0c1b52; }
.ring-gap { height: 44px; }
.ring-bar { display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; margin-top: 48px; }
.ring-bar h2 { font-size: 28px; font-weight: 800; letter-spacing: -.02em; }
.topics { margin: 0; padding: 0; background: none; }
.topic { background: rgba(255,255,255,.16); color: #fff; box-shadow: 0 5px 0 rgba(0,20,100,.35); }
.topic span { background: rgba(255,255,255,.22); color: #fff; }
.topic:hover { color: #fff; background: rgba(255,255,255,.26); }
.topic:active { transform: translateY(3px); box-shadow: 0 2px 0 rgba(0,20,100,.35); }
.topic.on { background: #fff; color: #0c1b52; box-shadow: 0 5px 0 #aebfee; }
.topic.on span { background: #eaf0ff; color: #1d54e0; }
.ring { position: relative; height: 430px; perspective: 1700px; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
.spin { position: absolute; left: 50%; top: 46%; width: 290px; height: 240px; margin: -120px 0 0 -145px; transform-style: preserve-3d; }
.ritem { position: absolute; inset: 0; transform-style: preserve-3d; transform: rotateY(calc(var(--i) * var(--step))) translateZ(var(--R)); }
.rc { position: absolute; inset: 0; display: block; color: #0c1b52; transform-style: preserve-3d; }
.rf {
  position: absolute; inset: 0; display: flex; flex-direction: column; gap: 9px; padding: 20px; border-radius: 22px;
  background: #fff; transform: translateZ(12px); backface-visibility: hidden; opacity: var(--o, 1);
}
.rb { position: absolute; inset: 0; border-radius: 22px; background: #9db3ee; transform: translateZ(-12px) rotateY(180deg); opacity: var(--o, 1); }
.rs { position: absolute; background: linear-gradient(90deg, #7f9be6, #a9bdf2); opacity: var(--o, 1); }
.rs.l { top: 22px; bottom: 22px; left: -12px; width: 24px; transform: rotateY(-90deg); }
.rs.r { top: 22px; bottom: 22px; left: calc(100% - 12px); width: 24px; transform: rotateY(90deg); }
.rf h3 { font-size: 18px; line-height: 1.28; letter-spacing: -.015em; }
.rf p { font-size: 13px; line-height: 1.55; color: #46557f; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.rf .time { margin-top: auto; color: #1d54e0; font-weight: 600; }
.deco { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.di { position: absolute; height: auto; animation: spin-in .8s cubic-bezier(.34,1.56,.64,1) both, bob 3.6s ease-in-out .8s infinite alternate; filter: drop-shadow(0 8px 8px rgba(0,10,80,.3)); }
.di.out { animation: spin-out .3s ease-in both; }
@keyframes spin-in { from { transform: rotate(-320deg) scale(0); opacity: 0; } to { transform: rotate(var(--r, 0deg)) scale(1); opacity: 1; } }
@keyframes spin-out { from { transform: rotate(var(--r, 0deg)) scale(1); opacity: 1; } to { transform: rotate(260deg) scale(0); opacity: 0; } }
@keyframes bob { to { translate: 0 -9px; } }
@media (max-width: 1000px) { .deco { display: none; } }
.rnav {
  position: absolute; top: 46%; width: 52px; height: 52px; margin-top: -26px; border: 0; border-radius: 50%; z-index: 5;
  background: #fff; color: #0c1b52; font-size: 24px; font-weight: 700; box-shadow: 0 7px 0 #aebfee, 0 16px 20px -8px rgba(0,10,80,.6);
}
.rnav:active { transform: translateY(4px); box-shadow: 0 3px 0 #aebfee; }
.rnav.l { left: 4px; } .rnav.r { right: 4px; }
header { background: rgba(23,59,158,.84); border-bottom: 1px solid rgba(255,255,255,.14); }
.logo { color: #fff; } .logo b { color: #ffd7bd; }
.nav-item { color: #dbe5ff; } .nav-item:hover { color: #fff; } .nav-item::before { background: #ff8a4c; }
.nav-item.on { color: #fff; }
header :focus-visible { outline-color: #fff; }
html { background: #173b9e; }
body { background: linear-gradient(180deg, #2756d6 0, #1f4cc4 45%, #173b9e 100%); }
.section { color: #fff; }
.section.tint { background: rgba(0,10,80,.2); }
.sec-head h2 { color: #fff; }
.sec-head h2::before { background: #ff8a4c; height: 3px; border-radius: 2px; }
.lead { color: #dbe5ff; }
.tabs { gap: 10px; margin-bottom: 26px; }
.tab { padding: 9px 18px; color: #fff; background: rgba(255,255,255,.16); border-radius: 999px; border-bottom: 0; box-shadow: 0 5px 0 rgba(0,20,100,.35); transition: transform .12s, box-shadow .12s, background .12s; }
.tab:hover { color: #fff; background: rgba(255,255,255,.26); }
.tab:active { transform: translateY(3px); box-shadow: 0 2px 0 rgba(0,20,100,.35); }
.tab.on { background: #fff; color: #0c1b52; box-shadow: 0 5px 0 #aebfee; }
.card { background: #fff; border: 0; border-radius: 28px; box-shadow: 0 10px 0 #9db3ee, 0 34px 36px -20px rgba(0,10,80,.7); color: #0c1b52; }
.card::after { display: none; }
.card h3 { color: #0c1b52; }
.card:hover { box-shadow: 0 10px 0 #9db3ee, 0 46px 46px -20px rgba(0,10,80,.8); }
.card:active { transform: translateY(6px); box-shadow: 0 4px 0 #9db3ee; }
.feature { background: #fff; color: #0c1b52; border-radius: 28px; box-shadow: 0 12px 0 #9db3ee, 0 38px 40px -20px rgba(0,10,80,.7); }
.feature p { color: #46557f; }
.feature .badge { background: var(--brand-soft); color: var(--brand-dk); }
.feature .lv3 { background: var(--brand-dk); color: #fff; }
.feature .lang { background: #eef1f7; color: #5b6273; }
.feature .lock { background: var(--warn-soft); color: var(--warn); }
.feature .time { color: #5b6273; }
.btn { background: #ff8a4c; color: #2a1608; border-radius: 999px; padding: 11px 22px; box-shadow: 0 5px 0 #c25a21; }
.feature:hover .btn { background: #ff9a62; }
.section.dark { background: #0b1a52; }
.empty { color: #dbe5ff; }
.hero p.ring-hint { text-align: center; font-size: 13px; color: #dbe5ff; max-width: none; margin: 0; padding-bottom: 30px; }
@media (max-width: 900px) { .ring { height: 400px; } .ring-bar h2 { font-size: 22px; } }
.card.soon { background: rgba(255,255,255,.14); color: #fff; box-shadow: inset 0 0 0 2px rgba(255,255,255,.4); min-height: 140px; }
.card.soon h3 { color: #fff; } .card.soon p { color: #dbe5ff; }
.card.soon .badge { background: rgba(255,255,255,.2); color: #fff; }
.card.soon:hover { transform: none; box-shadow: inset 0 0 0 2px rgba(255,255,255,.4); }
/* khoang cach gon hon */
.hero { padding: 40px 0 16px; }
.ring-gap { height: 20px; }
.ring { height: 330px; }
.spin { top: 50%; }
.rnav { top: 50%; }
.hero p.ring-hint { padding-bottom: 20px; }
.section { padding: 48px 0; }
.sec-head { margin-bottom: 24px; }
.sec-head h2 { font-size: 25px; }
.tabs { margin-bottom: 18px; }
.grid { gap: 20px; }
.split { gap: 20px; }
.dark-grid { gap: 32px; }
.feature { padding: 28px 28px 24px; }
footer { padding: 26px 0; }
@media (max-width: 900px) { .hero { padding: 32px 0 12px; } .ring { height: 330px; } .section { padding: 36px 0; } }
"""
D_JS = """
(function () {{
  var DATA = __RING__, spin = document.getElementById('spin'), ring = document.getElementById('ring');
  var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var list = [], step = 45, R = 400, cur = 0, tgt = 0, idx = 0, drag = null, moved = 0;
  function esc(t) {{ return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }}
  window.ringBuild = function (topic) {{
    list = DATA.filter(function (d) {{ return !topic || d.tp.indexOf(topic) > -1; }}).slice(0, 8);
    var n = Math.max(list.length, 5);
    step = 360 / n; R = Math.round(145 / Math.tan(Math.PI / n)) + 46;
    spin.style.setProperty('--step', step + 'deg'); spin.style.setProperty('--R', R + 'px');
    spin.innerHTML = list.map(function (d, i) {{
      return '<div class="ritem" style="--i:' + i + '"><a class="rc" href="' + d.u + '" target="_blank" rel="noopener" data-i="' + i + '"><div class="rf">' +
        '<div class="badges"><span class="badge ' + d.lv + '">' + esc(d.l) + '</span></div><h3>' + esc(d.t) + '</h3><p>' + esc(d.d) +
        '</p><span class="time">' + d.m + ' phút đọc</span></div><i class="rb"></i><i class="rs l"></i><i class="rs r"></i></a></div>';
    }}).join('');
    idx = 0; tgt = cur = 0; lastN = 0; if (typeof decorate === 'function') decorate();
  }};
  var ICONS = __ICONS__, lastN = -1, lastSet = [];
  // 10 vi tri co dinh (% cua vong): 5 ben trai, 5 ben phai doi xung qua truc giua, xep so le thanh mot cum gon.
  var SLOTS = [[10,22],[15,35],[10,48],[15,61],[10,74],[90,22],[85,35],[90,48],[85,61],[90,74]];
  function decorate() {{
    var pool = ICONS.map(function (_, i) {{ return i; }}).filter(function (i) {{ return lastSet.indexOf(i) < 0; }});
    pool.sort(function () {{ return Math.random() - .5; }});
    var pick = pool.slice(0, SLOTS.length), sizes = [32, 40, 48], el = document.getElementById('deco');
    [].forEach.call(el.children, function (c) {{ c.classList.add('out'); }});
    var html = pick.map(function (k, j) {{
      var sz = sizes[Math.floor(Math.random() * 3)], rot = Math.round(Math.random() * 40 - 20),
          x = SLOTS[j][0] + (Math.random() * 1.6 - .8), y = SLOTS[j][1] + (Math.random() * 1.6 - .8);
      return '<img class="di" alt="" src="' + ICONS[k] + '" style="width:' + sz + 'px;left:' + x.toFixed(1) + '%;top:' + y.toFixed(1) + '%;margin:-' + (sz / 2) + 'px 0 0 -' + (sz / 2) + 'px;--r:' + rot + 'deg;animation-delay:' + (j * .06) + 's,' + (.8 + j * .06) + 's">';
    }}).join('');
    setTimeout(function () {{ el.innerHTML = html; }}, el.children.length ? 300 : 0);
    lastSet = pick;
  }}
  function changed() {{
    var n = list.length || 1, k = ((idx % n) + n) % n;
    if (k !== lastN) {{ lastN = k; decorate(); }}
  }}
  function go(k) {{ idx += k; tgt = -idx * step; changed(); }}
  function frame() {{
    cur += (tgt - cur) * (calm ? 1 : .14);
    spin.style.transform = 'translateZ(' + (-R) + 'px) rotateY(' + cur + 'deg)';
    [].forEach.call(spin.children, function (it, i) {{
      var a = ((i * step + cur) % 360 + 540) % 360 - 180, cs = Math.cos(a * Math.PI / 180), c = it.firstChild;
      c.style.setProperty('--o', cs < .02 ? 0 : (.35 + .65 * cs).toFixed(2)); c.style.pointerEvents = cs < .02 ? 'none' : 'auto';
    }});
    requestAnimationFrame(frame);
  }}
  window.ringBuild(null); frame();
  document.getElementById('rprev').onclick = function () {{ go(-1); }};
  document.getElementById('rnext').onclick = function () {{ go(1); }};
  ring.addEventListener('pointerdown', function (e) {{ if (e.target.closest('.rnav')) return; drag = {{ x: e.clientX, t: tgt }}; moved = 0; }});
  addEventListener('pointermove', function (e) {{ if (!drag) return; var dx = e.clientX - drag.x; moved = Math.max(moved, Math.abs(dx)); tgt = drag.t + dx * .35; }});
  addEventListener('pointerup', function () {{ if (!drag) return; idx = Math.round(-tgt / step); tgt = -idx * step; drag = null; changed(); }});
  ring.addEventListener('click', function (e) {{
    var a = e.target.closest('.rc');
    if (moved > 6) {{ e.preventDefault(); moved = 0; return; }}
    if (!a) return;
    var n = list.length, i = +a.dataset.i, diff = ((i - (((idx % n) + n) % n)) % n + n) % n;
    if (diff > n / 2) diff -= n;
    if (diff !== 0) {{ e.preventDefault(); go(diff); }}
  }});
}})();
"""
_ring = sorted(all_docs, key=lambda d: d.get("created", ""), reverse=True)
RING_JSON = json.dumps(
    [{"t": d["title"], "d": d["desc"], "u": WIKI + d["token"], "tp": d.get("topics", []),
      "m": d["minutes"], "l": d["level"], "lv": LEVEL.get(d["level"], "lv1")} for d in _ring],
    ensure_ascii=False,
).replace("</", "<\\/")
import glob
ICON_JSON = json.dumps([_png("emoji-src/" + pathlib.Path(p).name) for p in sorted(glob.glob(str(HERE / "assets" / "emoji-src" / "emoji_*.png")))])
D_RING = f"""<div class="ring-gap"></div>
<div class="ring" id="ring"><div class="deco" id="deco"></div><div class="spin" id="spin"></div>
<button type="button" class="rnav l" id="rprev" aria-label="Thẻ trước">‹</button><button type="button" class="rnav r" id="rnext" aria-label="Thẻ sau">›</button></div>
<p class="ring-hint">Kéo để xoay · bấm thẻ bên cạnh để đưa ra trước · bấm thẻ chính để mở tài liệu. Các bài đầy đủ nằm bên dưới.</p>"""

HTML = HTML.replace(f'<div class="topics" role="group" aria-label="Lọc theo chủ đề">{topic_tabs}</div>', D_RING, 1)
HTML = HTML.replace("</style>", D_CSS.replace("{{", "{").replace("}}", "}") + "</style>", 1)
HTML = HTML.replace("</script>\n</body>", "</script>\n<script>" + D_JS.replace("{{", "{").replace("}}", "}").replace("__RING__", RING_JSON).replace("__ICONS__", ICON_JSON) + "</script>\n</body>", 1)
out = HERE / "index.html"
out.write_text(HTML, encoding="utf-8")
tpl = ", ".join(g["template"] for g in data["groups"])
print(f"wrote {out} ({len(HTML)} bytes) docs={total_docs}\nlayout: {tpl}")
