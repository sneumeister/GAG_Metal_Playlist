# -*- coding: utf-8 -*-
"""Standalone-HTML-Export der GAG Metal Playlist (inline CSS/JS, sortierbare Spalten)."""
from __future__ import annotations

import html
import json
from pathlib import Path

from .common import (
    HTML_NAME,
    ISSUES_NEW_CHOOSE_URL,
    MITMACHEN_INTRO,
    MITMACHEN_LINK_LABEL,
    compile_timestamp,
    json_status_date,
    link_or_empty,
    load_entries,
    output_dir,
    sorted_by_episode,
)


def _esc(text: object | None) -> str:
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def render_html(entries=None, *, compiled_at: str | None = None, json_date: str | None = None) -> str:
    if entries is None:
        entries = load_entries()
    entries = sorted_by_episode(entries)
    compiled_at = compiled_at or compile_timestamp()
    if json_date is None:
        json_date = json_status_date()
    json_line = json_date if json_date else "noch nicht gesetzt"

    payload = []
    for e in entries:
        payload.append(
            {
                "episodeId": e.get("episodeId"),
                "episodeUrl": link_or_empty(e.get("episodeUrl")),
                "episodeTitle": e.get("episodeTitle") or "",
                "band": e.get("band") or "",
                "songTitle": e.get("songTitle") or "",
                "matchTier": e.get("matchTier") or "",
                "justification": e.get("justification") or "",
                "youtubeUrl": link_or_empty(e.get("youtubeUrl")),
                "spotifyUrl": link_or_empty(e.get("spotifyUrl")),
            }
        )
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    col_count = 7

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GAG Metal Playlist</title>
<style>
:root {{
  --bg: #121417;
  --panel: #1c2128;
  --ink: #e8eaed;
  --muted: #9aa0a6;
  --line: #2d333b;
  --head: #0d1117;
  --accent: #e85d4c;
  --row-alt: #161b22;
  --hover: #242b33;
  --justify-bg: #0f1419;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: "Segoe UI", system-ui, sans-serif;
  background: radial-gradient(ellipse at top, #1a222c 0%, var(--bg) 55%);
  color: var(--ink);
  line-height: 1.45;
  min-height: 100vh;
}}
main {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}}
h1 {{
  margin: 0 0 0.4rem;
  font-size: 1.75rem;
  letter-spacing: 0.02em;
}}
.meta {{
  color: var(--muted);
  font-size: 0.95rem;
  margin-bottom: 1.25rem;
}}
.meta div {{ margin: 0.15rem 0; }}
.wrap {{
  overflow-x: auto;
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 4px;
}}
table {{
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  min-width: 720px;
}}
col.col-folge {{ width: 4.5rem; }}
col.col-episode {{ width: 28%; }}
col.col-band {{ width: 16%; }}
col.col-song {{ width: 22%; }}
col.col-stufe {{ width: 4.75rem; }}
col.col-link {{ width: 5rem; }}
th, td {{
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
  overflow-wrap: break-word;
}}
th {{
  background: var(--head);
  color: #f0f3f6;
  font-weight: 600;
  white-space: nowrap;
  user-select: none;
}}
th.sortable {{
  cursor: pointer;
}}
th.sortable:hover {{
  background: #21262d;
}}
th .arrow {{
  margin-left: 0.35rem;
  opacity: 0.85;
  font-size: 0.85em;
}}
td.folge {{
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}}
td.title {{
  overflow-wrap: anywhere;
}}
tr.row-main.alt td {{ background: var(--row-alt); }}
tr.row-main:hover td {{ background: var(--hover); }}
a {{
  color: var(--accent);
  text-decoration: none;
}}
a:hover {{ text-decoration: underline; }}
.links {{
  text-align: center;
  white-space: nowrap;
}}
td.stufe {{
  text-align: center;
  white-space: nowrap;
}}
button.stufe-btn {{
  appearance: none;
  margin: 0;
  padding: 0.35rem 0.45rem;
  min-width: 2.25rem;
  min-height: 2.25rem;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--accent);
  font: inherit;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-decoration: underline;
  text-underline-offset: 0.18em;
  cursor: pointer;
  touch-action: manipulation;
}}
button.stufe-btn:hover,
button.stufe-btn[aria-expanded="true"] {{
  background: transparent;
  color: #f08a7c;
}}
button.stufe-btn:focus-visible {{
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}}
tr.row-justification td {{
  background: var(--justify-bg);
  color: #c8cdd3;
  font-size: 0.92rem;
  padding: 0.65rem 0.85rem 0.85rem;
  border-bottom: 1px solid var(--line);
  overflow-wrap: anywhere;
  word-break: break-word;
}}
tr.row-justification[hidden] {{
  display: none;
}}
.justification-label {{
  display: block;
  color: var(--muted);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}}
.legend {{
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0 0 1.25rem;
}}
.legend p {{
  margin: 0.2rem 0;
}}
</style>
</head>
<body>
<main>
  <h1>GAG Metal Playlist</h1>
  <div class="meta">
    <div><strong>Compile-Datum:</strong> {_esc(compiled_at)}</div>
    <div><strong>JSON-Status:</strong> {_esc(json_line)}</div>
    <div>{_esc(MITMACHEN_INTRO)} <a href="{_esc(ISSUES_NEW_CHOOSE_URL)}">{_esc(MITMACHEN_LINK_LABEL)}</a></div>
  </div>
  <div class="legend">
    <p><strong>Stufe A</strong> – Exact: dieselbe Person / Schlacht / benanntes Ereignis (gleicher Erzählfokus).</p>
    <p><strong>Stufe B</strong> – Strong: eng verwandte Entity oder gleicher Kern mit abweichendem Fokus.</p>
    <p>Stufe anklicken, um die Begründung ein- oder auszublenden.</p>
  </div>
  <div class="wrap">
    <table id="playlist">
      <colgroup>
        <col class="col-folge">
        <col class="col-episode">
        <col class="col-band">
        <col class="col-song">
        <col class="col-stufe">
        <col class="col-link">
        <col class="col-link">
      </colgroup>
      <thead>
        <tr>
          <th class="sortable" data-key="episodeId" data-type="number">Folge<span class="arrow"></span></th>
          <th class="sortable" data-key="episodeTitle" data-type="string">Folgentitel<span class="arrow"></span></th>
          <th class="sortable" data-key="band" data-type="string">Band<span class="arrow"></span></th>
          <th class="sortable" data-key="songTitle" data-type="string">Song Titel<span class="arrow"></span></th>
          <th class="sortable" data-key="matchTier" data-type="string">Stufe<span class="arrow"></span></th>
          <th>YouTube</th>
          <th>Spotify</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</main>
<script type="application/json" id="playlist-data">{data_json}</script>
<script>
(function () {{
  const raw = document.getElementById("playlist-data").textContent;
  let rows = JSON.parse(raw);
  const tbody = document.querySelector("#playlist tbody");
  const headers = Array.from(document.querySelectorAll("th.sortable"));
  const colCount = {col_count};
  let sortKey = "episodeId";
  let sortDir = "asc";
  let sortType = "number";

  function linkCell(url, label) {{
    if (!url) return "—";
    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = label;
    return a;
  }}

  function render() {{
    tbody.replaceChildren();
    rows.forEach((r, index) => {{
      const tr = document.createElement("tr");
      tr.className = "row-main" + (index % 2 === 1 ? " alt" : "");

      const tdFolge = document.createElement("td");
      tdFolge.className = "folge";
      const epLabel = r.episodeId == null ? "?" : String(r.episodeId);
      if (r.episodeUrl) {{
        tdFolge.appendChild(linkCell(r.episodeUrl, epLabel));
      }} else {{
        tdFolge.textContent = epLabel;
      }}
      tr.appendChild(tdFolge);

      const tdTitle = document.createElement("td");
      tdTitle.className = "title";
      tdTitle.textContent = r.episodeTitle || "";
      tr.appendChild(tdTitle);

      const tdBand = document.createElement("td");
      tdBand.textContent = r.band || "";
      tr.appendChild(tdBand);

      const tdSong = document.createElement("td");
      tdSong.textContent = r.songTitle || "";
      tr.appendChild(tdSong);

      const tdStufe = document.createElement("td");
      tdStufe.className = "stufe";
      const tier = r.matchTier || "";
      const justification = (r.justification || "").trim();

      const detail = document.createElement("tr");
      detail.className = "row-justification";
      detail.setAttribute("hidden", "");
      const tdDetail = document.createElement("td");
      tdDetail.colSpan = colCount;
      const label = document.createElement("span");
      label.className = "justification-label";
      label.textContent = "Begründung";
      tdDetail.appendChild(label);
      tdDetail.appendChild(document.createTextNode(justification || "—"));
      detail.appendChild(tdDetail);

      if (tier && justification) {{
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "stufe-btn";
        btn.textContent = tier;
        btn.setAttribute("aria-expanded", "false");
        btn.setAttribute(
          "aria-label",
          "Begründung zu Stufe " + tier + " ein- oder ausblenden"
        );
        btn.addEventListener("click", () => {{
          const open = detail.hasAttribute("hidden");
          if (open) {{
            detail.removeAttribute("hidden");
            btn.setAttribute("aria-expanded", "true");
          }} else {{
            detail.setAttribute("hidden", "");
            btn.setAttribute("aria-expanded", "false");
          }}
        }});
        tdStufe.appendChild(btn);
      }} else {{
        tdStufe.textContent = tier || "—";
      }}
      tr.appendChild(tdStufe);

      const tdYt = document.createElement("td");
      tdYt.className = "links";
      const yt = linkCell(r.youtubeUrl, "link");
      if (typeof yt === "string") tdYt.textContent = yt; else tdYt.appendChild(yt);
      tr.appendChild(tdYt);

      const tdSp = document.createElement("td");
      tdSp.className = "links";
      const sp = linkCell(r.spotifyUrl, "link");
      if (typeof sp === "string") tdSp.textContent = sp; else tdSp.appendChild(sp);
      tr.appendChild(tdSp);

      tbody.appendChild(tr);
      tbody.appendChild(detail);
    }});
    updateArrows();
  }}

  function cmp(a, b) {{
    let av = a[sortKey];
    let bv = b[sortKey];
    if (sortType === "number") {{
      av = av == null ? Number.POSITIVE_INFINITY : Number(av);
      bv = bv == null ? Number.POSITIVE_INFINITY : Number(bv);
      return av - bv;
    }}
    av = (av == null ? "" : String(av)).toLocaleLowerCase("de");
    bv = (bv == null ? "" : String(bv)).toLocaleLowerCase("de");
    return av.localeCompare(bv, "de");
  }}

  function sortRows() {{
    rows = rows.slice().sort((a, b) => {{
      const c = cmp(a, b);
      return sortDir === "asc" ? c : -c;
    }});
    render();
  }}

  function updateArrows() {{
    for (const th of headers) {{
      const arrow = th.querySelector(".arrow");
      if (!arrow) continue;
      if (th.dataset.key === sortKey) {{
        arrow.textContent = sortDir === "asc" ? "▲" : "▼";
      }} else {{
        arrow.textContent = "";
      }}
    }}
  }}

  for (const th of headers) {{
    th.addEventListener("click", () => {{
      const key = th.dataset.key;
      const type = th.dataset.type || "string";
      if (sortKey === key) {{
        sortDir = sortDir === "asc" ? "desc" : "asc";
      }} else {{
        sortKey = key;
        sortType = type;
        sortDir = "asc";
      }}
      sortRows();
    }});
  }}

  sortRows();
}})();
</script>
</body>
</html>
"""


def write_html(out_path: Path | None = None) -> Path:
    path = out_path or (output_dir() / HTML_NAME)
    path.write_text(render_html(), encoding="utf-8")
    return path
