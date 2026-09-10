#!/usr/bin/env python3
"""Doc content.json roi sinh ra index.html (mot file tu chua, khong CDN).

Ba nhom layout, khong hon:
  split  1 the lon "doc truoc" + cac the con      (chi nhom dau)
  grid   luoi the doc dong nhat, co the kem tab loc (moi nhom giua)
  dark   dai mau dam: kenh ho tro + danh sach doc  (chi nhom cuoi)
Danh tinh moi nhom nam o header + nen tint, khong o kieu bo cuc.
"""
import json
import html
import pathlib
import urllib.parse

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
meta = data["meta"]
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


def esc(s):
    return html.escape(str(s), quote=True)


def docs_of(group):
    if "subgroups" in group:
        return [d for sg in group["subgroups"] for d in sg["docs"]]
    return group["docs"]


total_docs = sum(len(docs_of(g)) for g in data["groups"])

LEVEL = {"Cơ bản": "lv1", "Trung cấp": "lv2", "Nâng cao": "lv3"}


def attrs(doc):
    """Thuoc tinh chung cho moi phan tu tai lieu, dung cho tim kiem va loc."""
    aud = " ".join(doc["audience"])
    hay = f'{doc["title"]} {doc["desc"]} {doc["level"]} {doc["lang"]}'.lower()
    return (
        f'href="{WIKI}{esc(doc["token"])}" target="_blank" rel="noopener" '
        f'data-aud="{esc(aud)}" data-hay="{esc(hay)}"'
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
for g in data["groups"]:
    navs.append(
        f'<a class="nav-item" href="#{esc(g["id"])}" data-nav="{esc(g["id"])}">{esc(g["name"])}</a>'
    )
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
        <h2>{esc(g['name'])}</h2>
        <p class="lead">{esc(g['lead'])}</p>
      </div>
{TEMPLATES[g['template']](g)}    </div>
  </section>
"""
    )

chips = "".join(
    f'<button type="button" class="chip" data-chip="{esc(a["id"])}">{esc(a["label"])}</button>'
    for a in data["audiences"]
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

/* ============ hero ============ */
.hero {{ padding: 76px 0 54px; }}
.hero-in {{ border-left: 3px solid var(--brand); padding-left: 26px; }}
.hero h1 {{ font-size: 40px; line-height: 1.16; letter-spacing: -.03em; font-weight: 700; }}
.hero h1 em {{ font-style: normal; color: var(--brand); }}
.hero p {{ margin-top: 14px; font-size: 16px; color: var(--muted); max-width: 62ch; }}
.stats {{ display: flex; gap: 46px; flex-wrap: wrap; margin-top: 34px; }}
.stat b {{ display: block; font-size: 26px; font-weight: 700; letter-spacing: -.02em; }}
.stat span {{ font-size: 12.5px; color: var(--muted); }}

.controls {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 40px; }}
#q {{
  flex: 1; min-width: 250px; padding: 12px 16px; font: inherit; font-size: 14px;
  border: 1px solid var(--line); border-radius: var(--r-sm); outline: none; color: var(--text);
  background: #fff; transition: border-color .2s, box-shadow .2s;
}}
#q:focus {{ border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-soft); }}
#q::placeholder {{ color: var(--muted); }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.chip {{
  -webkit-appearance: none; appearance: none;
  padding: 9px 16px; font: inherit; font-size: 13px; font-weight: 500; color: var(--muted);
  background: #fff; border: 1px solid var(--line); border-radius: var(--r-full); cursor: pointer;
  transition: border-color .18s, color .18s, background .18s;
}}
.chip:hover {{ border-color: var(--brand); color: var(--brand); }}
.chip.on {{ background: var(--brand); border-color: var(--brand); color: #fff; }}

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
  padding: 0 0 5px; font-size: 13.5px; font-weight: 600; color: var(--muted); cursor: pointer;
  border-bottom: 2px solid transparent; transition: color .2s, border-color .2s;
}}
.tab:hover {{ color: var(--text); }}
.tab.on {{ color: var(--brand); border-bottom-color: var(--brand); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(258px, 1fr)); gap: 16px; }}
.card {{
  display: flex; flex-direction: column; gap: 9px; padding: 22px 20px 17px; background: #fff;
  border: 1px solid var(--line); border-radius: var(--r-md); position: relative; overflow: hidden;
  transition: transform .2s, box-shadow .2s, border-color .2s;
}}
.card::before {{
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--brand);
  transform: scaleY(0); transform-origin: top; transition: transform .28s ease;
}}
.card:hover {{ transform: translateY(-3px); border-color: #d3ddf5; box-shadow: 0 14px 32px rgba(1,20,62,.10); }}
.card:hover::before {{ transform: scaleY(1); }}
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
  .hero {{ padding: 48px 0 36px; }}
  .hero h1 {{ font-size: 30px; }}
  .split, .dark-grid {{ grid-template-columns: 1fr; }}
  .section {{ padding: 54px 0; }}
}}
@media (max-width: 600px) {{
  .wrap {{ padding: 0 16px; }}
  .head-in {{ gap: 16px; }}
  .stats {{ gap: 26px; }}
  .stat b {{ font-size: 21px; }}
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
    <span class="logo">Vietnamese <b>Lark's</b> library</span>
    <nav>{''.join(navs)}</nav>
  </div>
</header>

<div class="wrap hero">
  <div class="hero-in">
    <h1>Thư viện Lark <em>tiếng Việt</em></h1>
    <p>{esc(meta['subtitle'])}</p>
  </div>
  <div class="stats">
    <div class="stat"><b>{total_docs}</b><span>tài liệu</span></div>
    <div class="stat"><b>{len(data['groups'])}</b><span>chủ đề</span></div>
    <div class="stat"><b>{esc(meta['updated'])}</b><span>cập nhật gần nhất</span></div>
  </div>
  <div class="controls">
    <input id="q" type="search" placeholder="Tìm theo tên tài liệu, chủ đề, từ khoá..." autocomplete="off">
    <div class="chips">{chips}</div>
  </div>
</div>

{''.join(sections)}
<div class="wrap"><div class="empty" id="empty">Không có tài liệu nào khớp. Thử từ khoá khác hoặc bỏ bộ lọc vai trò.</div></div>

<footer>
  <div class="wrap">
    {esc(meta['credit'])}.<br>
    Nguồn: knowledge base <b>Lark - Vietnamese Library</b>. Nội dung chi tiết nằm trong tài liệu gốc trên Lark, trang này chỉ là mục lục.<br>
    Thẻ gắn nhãn <b>Cần quyền truy cập</b> hiện chưa mở chia sẻ ra ngoài tổ chức, vui lòng liên hệ người phụ trách. Cập nhật {esc(meta['updated'])}.
  </div>
</footer>

<script>
(function () {{
  var q = document.getElementById('q');
  var chips = [].slice.call(document.querySelectorAll('.chip'));
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  var items = [].slice.call(document.querySelectorAll('.item'));
  var sections = [].slice.call(document.querySelectorAll('.section'));
  var navs = [].slice.call(document.querySelectorAll('.nav-item'));
  var empty = document.getElementById('empty');
  var aud = null, tab = 'all';

  function norm(s) {{
    return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/đ/g, 'd');
  }}

  function apply() {{
    var term = norm(q.value.trim());
    var shown = 0;
    items.forEach(function (el) {{
      var okT = !term || norm(el.dataset.hay).indexOf(term) > -1;
      var okA = !aud || el.dataset.aud.split(' ').indexOf(aud) > -1;
      var okG = !el.dataset.sg || tab === 'all' || el.dataset.sg === tab;
      var on = okT && okA && okG;
      el.classList.toggle('hide', !on);
      if (on) shown++;
    }});
    sections.forEach(function (s) {{
      s.classList.toggle('hide', s.querySelectorAll('.item:not(.hide)').length === 0);
    }});
    navs.forEach(function (n) {{
      var sec = document.getElementById(n.dataset.nav);
      n.classList.toggle('hide', !!sec && sec.classList.contains('hide'));
    }});
    empty.style.display = shown === 0 ? 'block' : 'none';
  }}

  q.addEventListener('input', apply);
  chips.forEach(function (c) {{
    c.addEventListener('click', function () {{
      aud = aud === c.dataset.chip ? null : c.dataset.chip;
      chips.forEach(function (o) {{ o.classList.toggle('on', o.dataset.chip === aud); }});
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
      navs.forEach(function (n) {{ n.classList.toggle('on', n.dataset.nav === e.target.id); }});
    }});
  }}, {{ rootMargin: '-20% 0px -70% 0px' }});
  sections.forEach(function (s) {{ io.observe(s); }});
}})();
</script>
</body>
</html>
"""

out = HERE / "index.html"
out.write_text(HTML, encoding="utf-8")
tpl = ", ".join(g["template"] for g in data["groups"])
print(f"wrote {out} ({len(HTML)} bytes) docs={total_docs}\nlayout: {tpl}")
