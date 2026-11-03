"""Render grading results as a self-contained HTML page.

The output is an HTML fragment (title, style, content, script) that opens in
any browser and can also be published as a claude.ai Artifact unchanged.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

CSS = r"""
/* Layout: one reading column; each multiple is a section with its scorecard table, then its by-year chart. */
:root {
  --bg: #f7f8f7; --surface: #ffffff; --fg: #141716; --fg-2: #4d5451; --muted: #848b87;
  --rule: #e2e5e3; --axis: #c4c9c6; --accent: #2a6fdb; --accent-wash: #e8f0fc;
  --good: #1f7a3a; --bad: #b3362e; --warn-bg: #fff5d6; --warn-fg: #6b4e00;
  --s-market: #b4b9b6; --s-industry: #6f7672; --s-1: #2a78d6; --s-2: #eb6834; --s-3: #1baf7a;
  --font-text: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-data: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #121413; --surface: #1a1d1c; --fg: #eef0ef; --fg-2: #bcc2bf; --muted: #8a918d;
  --rule: #2b2f2d; --axis: #3b403e; --accent: #5b9bf0; --accent-wash: #1c2a3f;
  --good: #4cc26e; --bad: #f07a70; --warn-bg: #3a3112; --warn-fg: #f2d27a;
  --s-market: #5d6461; --s-industry: #9aa19d; --s-1: #3987e5; --s-2: #d95926; --s-3: #199e70;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #121413; --surface: #1a1d1c; --fg: #eef0ef; --fg-2: #bcc2bf; --muted: #8a918d;
  --rule: #2b2f2d; --axis: #3b403e; --accent: #5b9bf0; --accent-wash: #1c2a3f;
  --good: #4cc26e; --bad: #f07a70; --warn-bg: #3a3112; --warn-fg: #f2d27a;
  --s-market: #5d6461; --s-industry: #9aa19d; --s-1: #3987e5; --s-2: #d95926; --s-3: #199e70;
  color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-text); font-size: 15px; line-height: 1.55; }
.page { max-width: 980px; margin: 0 auto; padding-block: 40px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 36px; }
header { display: grid; gap: 10px; }
.eyebrow { font-family: var(--font-data); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
h1 { font-size: 30px; line-height: 1.15; margin: 0; font-weight: 600; text-wrap: balance; }
h2 { font-size: 21px; margin: 0; font-weight: 600; text-wrap: balance; }
h3 { font-size: 15px; margin: 0; font-weight: 600; }
p { margin: 0; max-width: 68ch; color: var(--fg-2); }
.notice { background: var(--warn-bg); color: var(--warn-fg); border-radius: 6px; padding: 10px 14px; font-size: 14px; max-width: 68ch; }
.protocol { display: flex; flex-wrap: wrap; gap: 8px; font-family: var(--font-data); font-size: 13px; }
.protocol span { border: 1px solid var(--rule); background: var(--surface); border-radius: 4px; padding: 4px 10px; color: var(--fg-2); }
.protocol .sealed { border-style: dashed; color: var(--muted); }
section { display: grid; gap: 16px; }
.lede { color: var(--fg); }
.table-wrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; min-width: 760px; }
th, td { padding: 9px 12px; text-align: right; border-bottom: 1px solid var(--rule); white-space: nowrap; }
th:first-child, td:first-child { text-align: left; white-space: normal; }
thead th { font-weight: 500; font-size: 12px; color: var(--muted); vertical-align: bottom; }
thead tr.group th { border-bottom: 0; padding-bottom: 0; text-transform: uppercase; letter-spacing: .06em; font-size: 11px; }
tbody tr:last-child td { border-bottom: 0; }
td.num { font-family: var(--font-data); font-variant-numeric: tabular-nums; }
sub { font-size: .75em; }
tr.baseline td:first-child { color: var(--fg-2); }
tr.best { background: var(--accent-wash); }
.tag { font-family: var(--font-data); font-size: 11px; color: var(--muted); margin-left: 6px; }
.pos { color: var(--good); } .neg { color: var(--bad); }
.sig { font-weight: 600; }
.chart { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 14px 14px 8px; position: relative; display: grid; gap: 8px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 13px; color: var(--fg-2); }
.legend i { display: inline-block; width: 14px; height: 2px; border-radius: 1px; vertical-align: middle; margin-right: 6px; }
.chart svg { width: 100%; height: auto; display: block; overflow: visible; }
.chart text { font-family: var(--font-data); font-size: 11px; fill: var(--muted); }
.chart text.end { fill: var(--fg-2); font-family: var(--font-text); font-size: 12px; }
.tip { position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--rule); border-radius: 6px;
  padding: 8px 10px; font-size: 12px; box-shadow: 0 4px 14px rgba(0,0,0,.12); min-width: 170px; }
.tip b { display: block; font-family: var(--font-data); margin-bottom: 4px; }
.tip div { display: flex; justify-content: space-between; gap: 12px; }
.tip span.v { font-family: var(--font-data); font-variant-numeric: tabular-nums; }
details { font-size: 14px; }
summary { cursor: pointer; color: var(--fg-2); }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
pre { background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 12px; overflow-x: auto;
  font-family: var(--font-data); font-size: 12.5px; line-height: 1.5; margin: 8px 0 0; color: var(--fg); }
.recipes { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.recipes > div { min-width: 0; }
.recipes p { font-size: 14px; margin-top: 4px; }
footer { font-size: 13px; color: var(--muted); display: grid; gap: 6px; }
footer p { color: var(--muted); }
"""

JS = r"""
(function () {
  const DATA = JSON.parse(document.getElementById('report-data').textContent);
  const NS = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const fmt = v => v == null ? '–' : v.toFixed(3);

  DATA.multiples.forEach((m, mi) => {
    const box = document.getElementById('chart-' + mi);
    if (!box) return;
    const W = 720, H = 280, L = 44, R = 150, T = 18, B = 28;
    const series = m.series;
    const years = [...new Set(series.flatMap(s => s.points.map(p => p[0])))].sort((a, b) => a - b);
    const vals = series.flatMap(s => s.points.map(p => p[1]));
    const ymax = Math.max(...vals) * 1.12, step = ymax > 0.4 ? 0.1 : 0.05;
    const top = Math.ceil(ymax / step) * step;
    const x = yr => L + (yr - years[0]) / Math.max(1, years.at(-1) - years[0]) * (W - L - R);
    const y = v => T + (1 - v / top) * (H - T - B);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img',
      'aria-label': `Median absolute valuation error by year, ${m.multiple}` }, box);

    // Validation window band.
    if (m.validate_years.length) {
      const a = x(m.validate_years[0]) - 8, b = x(m.validate_years.at(-1)) + 8;
      el('rect', { x: a, y: T, width: b - a, height: H - T - B, fill: 'var(--accent-wash)' }, svg);
      el('text', { x: a + 6, y: T + 13 }, svg).textContent = 'validate';
    }
    for (let v = 0; v <= top + 1e-9; v += step) {
      el('line', { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: v === 0 ? 'var(--axis)' : 'var(--rule)', 'stroke-width': 1 }, svg);
      el('text', { x: L - 8, y: y(v) + 4, 'text-anchor': 'end' }, svg).textContent = v.toFixed(2);
    }
    years.forEach((yr, i) => { if (i % 2 === 0 || i === years.length - 1)
      el('text', { x: x(yr), y: H - 8, 'text-anchor': 'middle' }, svg).textContent = yr; });

    const ends = [];
    series.forEach(s => {
      const d = s.points.map((p, i) => `${i ? 'L' : 'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join('');
      el('path', { d, fill: 'none', stroke: `var(${s.color})`, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, svg);
      const last = s.points.at(-1);
      el('circle', { cx: x(last[0]), cy: y(last[1]), r: 4, fill: `var(${s.color})`, stroke: 'var(--surface)', 'stroke-width': 2 }, svg);
      ends.push({ s, y: y(last[1]), x: x(last[0]) });
    });
    // Direct end labels; drop a label that would collide with a higher-priority one.
    ends.sort((a, b) => b.s.priority - a.s.priority);
    const placed = [];
    ends.forEach(e => { if (placed.every(p => Math.abs(p - e.y) >= 14)) {
      placed.push(e.y); el('text', { x: e.x + 10, y: e.y + 4, class: 'end' }, svg).textContent = e.s.short; } });

    // Hover: crosshair + tooltip with every series at the nearest year.
    const cross = el('line', { y1: T, y2: H - B, stroke: 'var(--axis)', 'stroke-width': 1, visibility: 'hidden' }, svg);
    const hit = el('rect', { x: L, y: T, width: W - L - R, height: H - T - B, fill: 'transparent' }, svg);
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; box.appendChild(tip);
    const show = evt => {
      const pt = svg.getBoundingClientRect(), sx = (evt.clientX - pt.left) * W / pt.width;
      const yr = years.reduce((a, b) => Math.abs(x(b) - sx) < Math.abs(x(a) - sx) ? b : a);
      cross.setAttribute('x1', x(yr)); cross.setAttribute('x2', x(yr)); cross.setAttribute('visibility', 'visible');
      tip.innerHTML = `<b>FY ${yr}</b>` + series.map(s => { const p = s.points.find(q => q[0] === yr);
        return `<div><span><i style="display:inline-block;width:10px;height:2px;background:var(${s.color});vertical-align:middle;margin-right:6px"></i>${s.short}</span><span class="v">${fmt(p && p[1])}</span></div>`; }).join('');
      tip.hidden = false;
      const bx = box.getBoundingClientRect(), px = evt.clientX - bx.left;
      tip.style.left = Math.min(px + 14, bx.width - tip.offsetWidth - 8) + 'px';
      tip.style.top = (evt.clientY - bx.top - 20) + 'px';
    };
    hit.addEventListener('pointermove', show);
    hit.addEventListener('pointerleave', () => { tip.hidden = true; cross.setAttribute('visibility', 'hidden'); });
  });
})();
"""

COLORS = {"market_median": "--s-market", "industry_median": "--s-industry"}
RECIPE_COLORS = ["--s-1", "--s-2", "--s-3"]


def _num(v, digits=3, signed=False, pct=False):
    if v is None or v != v:  # NaN
        return "–"
    if pct:
        return f"{v * 100:.1f}%"
    return f"{v:+.{digits}f}" if signed else f"{v:.{digits}f}"


def _gain_cell(gain, t):
    if gain is None or gain != gain:
        return '<td class="num">–</td>'
    cls = "pos" if gain > 0 else "neg"
    sig = " sig" if t == t and abs(t) >= 1.96 else ""
    return f'<td class="num {cls}{sig}">{_num(gain, signed=True)}</td>'


def render(results: dict) -> str:
    """results: output of scripts/run_comps.py (see that file for the schema)."""
    esc = html.escape
    p = results["protocol"]
    payload = _chart_payload(results)
    span = lambda ys: f"{ys[0]}–{ys[-1]}" if ys else "–"  # noqa: E731

    parts = [
        '<title>Comps Lab Results</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">',
        f"<style>{CSS}</style>",
        '<main class="page">',
        "<header>",
        f'<div class="eyebrow">ValuationLab · Track 1 · comps accuracy</div>',
        "<h1>Comps Lab Results</h1>",
        f'<p class="lede">{esc(results["headline"])}</p>',
    ]
    if results.get("synthetic"):
        parts.append('<div class="notice">Synthetic data: this run tests the pipeline. '
                     'The numbers say nothing about real markets.</div>')
    for note in results.get("notes", []):
        parts.append(f'<div class="notice">{esc(note)}</div>')
    parts += [
        '<div class="protocol">',
        f'<span>Data: {esc(results["dataset"])}</span>',
        f'<span>Explore FY {span(p["explore"])}</span>',
        f'<span>Validate FY {span(p["validate"])}</span>',
        f'<span class="sealed">Holdout FY {span(p["holdout"])} · sealed</span>',
        "</div>",
        "</header>",
    ]

    for mi, m in enumerate(results["multiples"]):
        rows = m["rows"]
        best = min((r for r in rows if r["kind"] == "recipe"),
                   key=lambda r: r["validate"]["median_abs_error"], default=None)
        parts += [
            "<section>",
            f'<h2>{esc(m["multiple"])}</h2>',
            f'<p>Error is |ln(V<sub>est</sub> / V)| for each firm-year, where V is the observed '
            f'{"enterprise value" if m["multiple"].startswith("EV") else "market capitalization"} '
            f'and V<sub>est</sub> the recipe\'s estimate. Gain is the yearly mean reduction in error versus the industry median, '
            f'with a Newey–West t-statistic over years, shown only when a period has at least 6 years. '
            f'Bold gains have |t| ≥ 1.96.</p>',
            '<div class="table-wrap"><table>',
            '<thead><tr class="group"><th></th><th colspan="2">Median |error|</th><th colspan="2">Validate</th>'
            '<th colspan="2">Gain vs industry median</th><th colspan="2">t-stat</th></tr>',
            "<tr><th>Recipe</th><th>Explore</th><th>Validate</th><th>Within ±15%</th><th>Coverage</th>"
            "<th>Explore</th><th>Validate</th><th>Explore</th><th>Validate</th></tr></thead><tbody>",
        ]
        for r in rows:
            e, v = r["explore"], r["validate"]
            ge, gv = e.get("vs", {}).get("industry_median", {}), v.get("vs", {}).get("industry_median", {})
            cls = "baseline" if r["kind"] == "baseline" else ("best" if r is best else "")
            tag = '<span class="tag">baseline</span>' if r["kind"] == "baseline" else ""
            parts.append(
                f'<tr class="{cls}"><td>{esc(r["name"])}{tag}</td>'
                f'<td class="num">{_num(e["median_abs_error"])}</td><td class="num">{_num(v["median_abs_error"])}</td>'
                f'<td class="num">{_num(v["within_15pct"], pct=True)}</td><td class="num">{_num(v["coverage"], pct=True)}</td>'
                + (_gain_cell(ge.get("mean_gain"), ge.get("t_stat", float("nan"))) if r["id"] != "industry_median" else '<td class="num">–</td>')
                + (_gain_cell(gv.get("mean_gain"), gv.get("t_stat", float("nan"))) if r["id"] != "industry_median" else '<td class="num">–</td>')
                + f'<td class="num">{_num(ge.get("t_stat"), 2)}</td><td class="num">{_num(gv.get("t_stat"), 2)}</td></tr>'
            )
        parts.append("</tbody></table></div>")

        legend = "".join(f'<span><i style="background:var({s["color"]})"></i>{esc(s["name"])}</span>'
                         for s in payload["multiples"][mi]["series"])
        parts += [
            f'<div class="chart" id="chart-{mi}"><h3>Median |error| by fiscal year</h3>'
            f'<div class="legend">{legend}</div></div>',
            "<details><summary>Recipe definitions</summary><div class=\"recipes\">",
        ]
        for r in rows:
            if r["kind"] != "recipe":
                continue
            parts.append(
                f'<div><h3>{esc(r["name"])}</h3>'
                + (f'<p>{esc(r["mechanism"])}</p>' if r.get("mechanism") else "")
                + f'<pre>{esc(json.dumps(r["spec"], indent=2))}</pre></div>'
            )
        parts += ["</div></details>", "</section>"]

    parts += [
        "<footer>",
        f'<p>Generated {esc(results["generated"])} · {results["n_rows"]:,} firm-years · peers exclude the target firm · '
        'recipes may not use a target\'s own market value as an input.</p>',
        "</footer>",
        "</main>",
        f'<script type="application/json" id="report-data">{json.dumps(payload).replace("</", "<\\/")}</script>',
        f"<script>{JS}</script>",
    ]
    return "\n".join(parts)


def _chart_payload(results: dict) -> dict:
    out = []
    for m in results["multiples"]:
        series, ri = [], 0
        for r in m["rows"]:
            if r["kind"] == "baseline":
                color, priority = COLORS.get(r["id"], "--s-market"), 0 if r["id"] == "market_median" else 1
            else:
                color, priority = RECIPE_COLORS[ri % len(RECIPE_COLORS)], 3 - ri
                ri += 1
            series.append({"name": r["name"], "short": r.get("short", r["name"])[:22],
                           "color": color, "priority": priority, "points": r["yearly"]})
        out.append({"multiple": m["multiple"], "validate_years": results["protocol"]["validate"], "series": series})
    return {"multiples": out}


def write(results: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(results), encoding="utf-8")
    return path
