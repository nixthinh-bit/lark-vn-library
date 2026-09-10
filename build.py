#!/usr/bin/env python3
"""Doc content.json roi sinh ra index.html (mot file tu chua, khong CDN).

Moi nhom dung mot layout rieng de trang khong bi lap:
  split  1 the lon + the phu       stack  stepper doc
  steps  3 buoc ngang               tabs   tab loc + luoi the
  rows   danh sach dong gon         dark   dai mau dam cuoi trang
"""
import json
import html
import pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
meta = data["meta"]
WIKI = meta["wiki_base"]


def esc(s):
    return html.escape(str(s), quote=True)


def docs_of(group):
    if "subgroups" in group:
        return [d for sg in group["subgroups"] for d in sg["docs"]]
    return group["docs"]


total_docs = sum(len(docs_of(g)) for g in data["groups"])
total_min = sum(d["minutes"] for g in data["groups"] for d in docs_of(g))

LEVEL = {"Cơ bản": "lv1", "Trung cấp": "lv2", "Nâng cao": "lv3"}


def attrs(doc):
    """Thuoc tinh chung cho moi phan tu tai lieu, dung cho tim kiem va loc."""
    aud = " ".join(doc["audience"])
    hay = f'{doc["title"]} {doc["desc"]} {doc["level"]} {doc["lang"]}'.lower()
    return (
        f'href="{WIKI}{esc(doc["token"])}" target="_blank" rel="noopener" '
        f'data-aud="{esc(aud)}" data-hay="{esc(hay)}"'
    )


def meta_row(doc, sep=" · "):
    bits = [
        f'<span class="badge {LEVEL.get(doc["level"], "lv1")}">{esc(doc["level"])}</span>',
        f'<span class="badge lang">{esc(doc["lang"])}</span>',
    ]
    if not doc["shared"]:
        bits.append('<span class="badge lock">Cần quyền truy cập</span>')
    return "".join(bits)


# ----------------------------------------------------------------- templates
def t_split(g):
    lead, *rest = g["docs"]
    side = "".join(
        f"""        <a class="mini item" {attrs(d)}>
          <div class="mini-badges">{meta_row(d)}</div>
          <h3>{esc(d['title'])}</h3>
          <p>{esc(d['desc'])}</p>
          <span class="go">Mở tài liệu →</span>
        </a>
"""
        for d in rest
    )
    return f"""      <div class="split">
        <a class="feature item" {attrs(lead)}>
          <span class="eyebrow-sm">Đọc trước tiên</span>
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


def t_steps(g):
    out = '      <div class="steps">\n'
    for i, d in enumerate(g["docs"], 1):
        out += f"""        <a class="step item" {attrs(d)}>
          <span class="step-n">{i:02d}</span>
          <h3>{esc(d['title'])}</h3>
          <p>{esc(d['desc'])}</p>
          <div class="step-foot">{meta_row(d)}<span class="time">{d['minutes']} phút</span></div>
        </a>
"""
    return out + "      </div>\n"


def t_stack(g):
    out = '      <div class="stack">\n'
    for i, d in enumerate(g["docs"], 1):
        out += f"""        <a class="rung item" {attrs(d)}>
          <span class="rung-n">{i}</span>
          <div class="rung-body">
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
            <div class="rung-foot">{meta_row(d)}<span class="time">{d['minutes']} phút đọc</span></div>
          </div>
          <span class="arrow">→</span>
        </a>
"""
    return out + "      </div>\n"


def t_rows(g):
    out = '      <div class="rows">\n'
    for d in g["docs"]:
        out += f"""        <a class="row item" {attrs(d)}>
          <div class="row-main">
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
          </div>
          <div class="row-meta">{meta_row(d)}<span class="time">{d['minutes']} phút</span></div>
          <span class="arrow">→</span>
        </a>
"""
    return out + "      </div>\n"


def t_panels(g):
    """Luoi 2 cot, moi muc chi co vien tren, khac nhip voi t_rows (khong dung 2 lan cung mot layout)."""
    out = '      <div class="panels">\n'
    for d in g["docs"]:
        out += f"""        <a class="panel item" {attrs(d)}>
          <div class="panel-head">
            <h3>{esc(d['title'])}</h3>
            <span class="arrow">→</span>
          </div>
          <p>{esc(d['desc'])}</p>
          <div class="panel-foot">{meta_row(d)}<span class="time">{d['minutes']} phút đọc</span></div>
        </a>
"""
    return out + "      </div>\n"


def card(d):
    return f"""          <a class="card item" {attrs(d)}>
            <div class="badges">{meta_row(d)}</div>
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
            <div class="card-foot"><span class="time">{d['minutes']} phút đọc</span><span class="go">Mở →</span></div>
          </a>
"""


def t_tabs(g):
    tabs = '<li class="tab on" data-tab="all">Tất cả</li>'
    body = ""
    for i, sg in enumerate(g["subgroups"]):
        key = f"sg{i}"
        tabs += f'<li class="tab" data-tab="{key}">{esc(sg["name"])}</li>'
        body += f'        <div class="grid" data-sg="{key}">\n'
        body += "".join(card(d) for d in sg["docs"])
        body += "        </div>\n"
    return f'      <ul class="tabs">{tabs}</ul>\n{body}'


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
          <h4 class="dsub">Tài liệu kèm theo</h4>
{links}        </div>
      </div>
"""


TEMPLATES = {
    "split": t_split,
    "steps": t_steps,
    "stack": t_stack,
    "rows": t_rows,
    "panels": t_panels,
    "tabs": t_tabs,
    "dark": t_dark,
}

# ------------------------------------------------------------------ assemble
navs, sections = [], []
for i, g in enumerate(data["groups"], 1):
    navs.append(
        f'<a class="nav-item" href="#{esc(g["id"])}" data-nav="{esc(g["id"])}">{esc(g["name"])}</a>'
    )
    cls = " ".join(
        filter(
            None,
            [
                "section",
                f'sec-{g["template"]}',
                "tint" if g.get("tint") else "",
                "dark" if g["template"] == "dark" else "",
                "center" if g.get("center") else "",
            ],
        )
    )
    sections.append(
        f"""  <section class="{cls}" id="{esc(g['id'])}">
    <div class="wrap">
      <div class="sec-head">
        <h2><span class="sec-ico">{esc(g['icon'])}</span>{esc(g['name'])}</h2>
        <p class="lead">{esc(g['lead'])}</p>
      </div>
{TEMPLATES[g['template']](g)}    </div>
  </section>
"""
    )

chips = "".join(
    f'<button class="chip" data-chip="{esc(a["id"])}">{esc(a["label"])}</button>'
    for a in data["audiences"]
)

HTML = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<title>{esc(meta['title'])}</title>
<style>
:root {{
  --bg: #ffffff;
  --tint: #f3f6fc;
  --ink: #01143e;
  --text: #10162b;
  --muted: #6a7183;
  --faint: #99a0b0;
  --line: #e6e9f0;
  --line-soft: #eef1f7;
  --brand: #3370ff;
  --brand-dk: #1d54e0;
  --brand-soft: #eaf0ff;
  --warn: #c9302c;
  --warn-soft: #fdeceb;
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
.hero .credit {{ margin-top: 8px; font-size: 12.5px; color: var(--faint); font-style: italic; }}
.stats {{ display: flex; gap: 46px; flex-wrap: wrap; margin-top: 34px; }}
.stat b {{ display: block; font-size: 26px; font-weight: 700; letter-spacing: -.02em; }}
.stat span {{ font-size: 11.5px; color: var(--faint); text-transform: uppercase; letter-spacing: .09em; }}

.controls {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 40px; }}
#q {{
  flex: 1; min-width: 250px; padding: 12px 16px; font: inherit; font-size: 14px;
  border: 1px solid var(--line); border-radius: 10px; outline: none; color: var(--text);
  background: #fff; transition: border-color .2s, box-shadow .2s;
}}
#q:focus {{ border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-soft); }}
#q::placeholder {{ color: var(--faint); }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.chip {{
  padding: 9px 16px; font: inherit; font-size: 13px; font-weight: 500; color: var(--muted);
  background: #fff; border: 1px solid var(--line); border-radius: 999px; cursor: pointer;
  transition: all .18s;
}}
.chip:hover {{ border-color: var(--brand); color: var(--brand); }}
.chip.on {{ background: var(--brand); border-color: var(--brand); color: #fff; }}
.hint {{ margin-top: 12px; font-size: 12.5px; color: var(--faint); }}

/* ============ section shell ============ */
.section {{ padding: 74px 0; scroll-margin-top: 62px; }}
.section.tint {{ background: var(--tint); }}
.sec-head {{ margin-bottom: 34px; max-width: 70ch; }}
.sec-head h2 {{
  font-size: 27px; font-weight: 700; letter-spacing: -.025em; position: relative;
  display: inline-flex; align-items: center; gap: 12px; padding-bottom: 9px;
}}
.sec-ico {{ font-size: 22px; line-height: 1; }}
.sec-head h2::before {{
  content: ""; position: absolute; left: 0; right: 42%; bottom: 0; height: 2px; background: var(--brand);
}}
.lead {{ margin-top: 10px; font-size: 14.5px; color: var(--muted); }}
.section.center .sec-head {{ margin-left: auto; margin-right: auto; text-align: center; }}
.section.center .sec-head h2 {{ justify-content: center; }}
.section.center .sec-head h2::before {{ left: 26%; right: 26%; }}

/* shared bits */
.badges, .mini-badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.badge {{ font-size: 10.5px; font-weight: 600; padding: 3px 8px; border-radius: 5px; white-space: nowrap; letter-spacing: .01em; }}
.lv1 {{ background: var(--brand-soft); color: var(--brand-dk); }}
.lv2 {{ background: #fff3e0; color: #b46b00; }}
.lv3 {{ background: #f1ebff; color: #6b3fd4; }}
.lang {{ background: #f2f4f8; color: var(--muted); }}
.lock {{ background: var(--warn-soft); color: var(--warn); }}
.time {{ font-size: 12px; color: var(--faint); white-space: nowrap; }}
.go {{ font-size: 12.5px; font-weight: 600; color: var(--brand); }}
.arrow {{ color: var(--faint); font-size: 17px; transition: transform .2s, color .2s; }}

/* ============ 01 split ============ */
.split {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; align-items: stretch; }}
.feature {{
  display: flex; flex-direction: column; gap: 12px; padding: 34px 34px 30px;
  background: var(--ink); border-radius: 16px; color: #fff; position: relative; overflow: hidden;
  transition: transform .22s;
}}
.feature::after {{
  content: ""; position: absolute; right: -80px; top: -90px; width: 230px; height: 230px;
  border-radius: 50%; background: rgba(51,112,255,.22);
}}
.feature:hover {{ transform: translateY(-3px); }}
.eyebrow-sm {{ font-size: 10.5px; font-weight: 700; letter-spacing: .16em; color: #7ea3ff; text-transform: uppercase; }}
.feature h3 {{ font-size: 25px; line-height: 1.25; letter-spacing: -.02em; position: relative; }}
.feature p {{ font-size: 14px; color: #b9c3d8; line-height: 1.65; flex: 1; position: relative; }}
.feature-foot {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; position: relative; }}
.feature .badge {{ background: rgba(255,255,255,.14); color: #dce4f5; }}
.feature .lock {{ background: rgba(255,138,132,.2); color: #ffb3ae; }}
.feature .time {{ color: #8d99b4; }}
.btn {{
  align-self: flex-start; margin-top: 6px; padding: 10px 20px; border-radius: 8px;
  background: var(--brand); color: #fff; font-size: 13px; font-weight: 600; position: relative;
  transition: background .2s;
}}
.feature:hover .btn {{ background: #4a80ff; }}
.split-side {{ display: flex; flex-direction: column; gap: 20px; }}
.mini {{
  flex: 1; display: flex; flex-direction: column; gap: 9px; padding: 24px 24px 20px;
  border: 1px solid var(--line); border-radius: 14px; background: #fff;
  transition: border-color .2s, box-shadow .2s;
}}
.mini:hover {{ border-color: var(--brand); box-shadow: 0 10px 28px rgba(51,112,255,.10); }}
.mini h3 {{ font-size: 17px; letter-spacing: -.015em; }}
.mini p {{ font-size: 13.5px; color: var(--muted); flex: 1; }}

/* ============ 02 steps ============ */
.steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; position: relative; }}
.steps::before {{
  content: ""; position: absolute; left: 8%; right: 8%; top: 42px; height: 1px;
  background: repeating-linear-gradient(90deg, var(--faint) 0 5px, transparent 5px 11px); opacity: .45;
}}
.step {{
  position: relative; background: #fff; border: 1px solid var(--line); border-radius: 14px;
  padding: 24px 22px 20px; display: flex; flex-direction: column; gap: 9px; overflow: hidden;
  transition: transform .2s, box-shadow .2s;
}}
.step::after {{
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 3px; width: 46px;
  margin: auto; background: var(--brand); transition: width .4s ease;
}}
.step:hover {{ transform: translateY(-3px); box-shadow: 0 12px 30px rgba(1,20,62,.09); }}
.step:hover::after {{ width: 100%; }}
.step-n {{
  font-size: 30px; font-weight: 800; letter-spacing: -.04em; color: var(--brand);
  opacity: .22; line-height: 1;
}}
.step h3 {{ font-size: 17px; letter-spacing: -.015em; }}
.step p {{ font-size: 13.5px; color: var(--muted); flex: 1; }}
.step-foot {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; padding-top: 10px; border-top: 1px solid var(--line-soft); }}
.step-foot .time {{ margin-left: auto; }}

/* ============ 03 rows ============ */
.rows {{ border-top: 1px solid var(--line); }}
.row {{
  display: flex; align-items: center; gap: 24px; padding: 22px 18px;
  border-bottom: 1px solid var(--line); transition: background .18s, padding-left .18s;
}}
.row:hover {{ background: #fff; padding-left: 26px; }}
.section.tint .row:hover {{ background: #fff; }}
.section:not(.tint) .row:hover {{ background: var(--tint); }}
.row-main {{ flex: 1; min-width: 0; }}
.row-main h3 {{ font-size: 16.5px; letter-spacing: -.015em; }}
.row-main p {{ font-size: 13.5px; color: var(--muted); margin-top: 3px; }}
.row-meta {{ display: flex; gap: 7px; align-items: center; flex-wrap: wrap; justify-content: flex-end; flex: 0 0 296px; }}
.row:hover .arrow {{ transform: translateX(5px); color: var(--brand); }}

/* ============ 03b panels (2-col, distinct rhythm from rows) ============ */
.panels {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 32px; }}
.panel {{
  padding: 20px 4px 22px; border-top: 1px solid var(--line); transition: border-color .18s;
}}
.panel:hover {{ border-color: var(--brand); }}
.panel-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }}
.panel-head h3 {{ font-size: 16.5px; letter-spacing: -.015em; }}
.panel-head .arrow {{ flex: 0 0 auto; }}
.panel:hover .arrow {{ transform: translateX(4px); color: var(--brand); }}
.panel p {{ font-size: 13.5px; color: var(--muted); margin: 6px 0 12px; }}
.panel-foot {{ display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }}
.panel-foot .time {{ margin-left: auto; }}

/* ============ 04 stack ============ */
.stack {{ display: flex; flex-direction: column; gap: 14px; }}
.rung {{
  display: flex; gap: 22px; align-items: center; background: #fff; border: 1px solid var(--line);
  border-left: 3px solid var(--brand); border-radius: 12px; padding: 22px 24px;
  transition: transform .2s, box-shadow .2s;
}}
.rung:hover {{ transform: translateX(5px); box-shadow: 0 10px 26px rgba(1,20,62,.08); }}
.rung-n {{
  flex: 0 0 42px; height: 42px; border-radius: 50%; background: var(--brand-soft); color: var(--brand-dk);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px;
}}
.rung-body {{ flex: 1; min-width: 0; }}
.rung-body h3 {{ font-size: 17px; letter-spacing: -.015em; }}
.rung-body p {{ font-size: 13.5px; color: var(--muted); margin: 4px 0 9px; }}
.rung-foot {{ display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }}
.rung:hover .arrow {{ transform: translateX(5px); color: var(--brand); }}

/* ============ 05 tabs + grid ============ */
.tabs {{ list-style: none; padding: 0; text-align: center; margin-bottom: 26px; }}
.tab {{
  display: inline-block; margin: 0 14px 8px; padding-bottom: 5px; font-size: 13.5px; font-weight: 600;
  color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; transition: all .2s;
}}
.tab:hover {{ color: var(--text); }}
.tab.on {{ color: var(--brand); border-bottom-color: var(--brand); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(258px, 1fr)); gap: 18px; margin-bottom: 18px; }}
.card {{
  display: flex; flex-direction: column; gap: 9px; padding: 22px 20px 17px; background: #fff;
  border: 1px solid var(--line); border-radius: 13px; position: relative; overflow: hidden;
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
.card .go {{ opacity: 0; transform: translateX(-4px); transition: all .2s; }}
.card:hover .go {{ opacity: 1; transform: none; }}

/* ============ 06 dark band ============ */
.section.dark {{ background: var(--ink); color: #fff; }}
.section.dark .lead {{ color: #a7b2c9; }}
.section.dark h2::before {{ background: #7ea3ff; }}
.dark-grid {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 44px; }}
.chans {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-content: start; }}
.chan {{
  padding: 18px 18px 16px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.1);
  border-radius: 11px; position: relative;
}}
.chan-n {{
  display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px;
  border-radius: 50%; background: rgba(126,163,255,.18); color: #9db8ff; font-size: 11.5px; font-weight: 700;
  margin-bottom: 8px;
}}
.chan b {{ display: block; font-size: 14.5px; margin: 0 0 5px; }}
.chan span {{ font-size: 12.5px; color: #a7b2c9; line-height: 1.55; }}
.dsub {{ font-size: 10.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #7ea3ff; margin-bottom: 12px; }}
.dlink {{
  display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 10px;
  padding: 13px 0; border-bottom: 1px solid rgba(255,255,255,.1); transition: padding-left .2s;
}}
.dlink:hover {{ padding-left: 8px; }}
.dlink-t {{ grid-column: 1; grid-row: 1; font-size: 14.5px; font-weight: 600; }}
.dlink-d {{
  grid-column: 1; grid-row: 2; font-size: 12.5px; color: #a7b2c9; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.dlink .arrow {{ grid-column: 2; grid-row: 1 / 3; align-self: center; color: #6b7891; }}
.dlink:hover .arrow {{ transform: translateX(4px); color: #fff; }}

/* ============ footer ============ */
footer {{ background: #000c26; color: #8791a8; padding: 34px 0; font-size: 12.5px; line-height: 1.75; }}
footer b {{ color: #c3ccdd; }}
.empty {{ display: none; padding: 70px 0; text-align: center; color: var(--faint); font-size: 14.5px; }}
.hide {{ display: none !important; }}

/* ============ responsive ============ */
@media (max-width: 900px) {{
  .hero {{ padding: 48px 0 36px; }}
  .hero h1 {{ font-size: 30px; }}
  .split, .dark-grid, .panels {{ grid-template-columns: 1fr; }}
  .panel {{ padding: 18px 0 20px; }}
  .steps {{ grid-template-columns: 1fr; }}
  .steps::before {{ display: none; }}
  .section {{ padding: 54px 0; }}
  .row {{ flex-wrap: wrap; gap: 12px; }}
  .row-meta {{ flex: 1 1 100%; justify-content: flex-start; }}
  .row .arrow {{ display: none; }}
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
  .rung {{ flex-wrap: wrap; gap: 14px; }}
  .rung .arrow {{ display: none; }}
  .card .go {{ opacity: 1; transform: none; }}
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
    <p class="credit">{esc(meta['credit'])}</p>
  </div>
  <div class="stats">
    <div class="stat"><b>{total_docs}</b><span>tài liệu</span></div>
    <div class="stat"><b>{len(data['groups'])}</b><span>chủ đề</span></div>
    <div class="stat"><b>~{round(total_min / 60)} giờ</b><span>tổng nội dung</span></div>
    <div class="stat"><b>{esc(meta['updated'])}</b><span>cập nhật</span></div>
  </div>
  <div class="controls">
    <input id="q" type="search" placeholder="Tìm theo tên tài liệu, chủ đề, từ khoá..." autocomplete="off">
    <div class="chips">{chips}</div>
  </div>
  <p class="hint">Chọn vai trò để lọc nhanh tài liệu liên quan tới bạn. Bấm lại để bỏ lọc.</p>
</div>

{''.join(sections)}
<div class="wrap"><div class="empty" id="empty">Không có tài liệu nào khớp. Thử từ khoá khác hoặc bỏ bộ lọc vai trò.</div></div>

<footer>
  <div class="wrap">
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
      var sg = el.closest('[data-sg]');
      var okG = !sg || tab === 'all' || sg.dataset.sg === tab;
      var on = okT && okA && okG;
      el.classList.toggle('hide', !on);
      if (on) shown++;
    }});
    document.querySelectorAll('[data-sg]').forEach(function (g) {{
      g.classList.toggle('hide', g.querySelectorAll('.item:not(.hide)').length === 0);
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
