# -*- coding: utf-8 -*-
"""Markdown-Export der GAG Metal Playlist."""
from __future__ import annotations

from pathlib import Path

from .common import (
    ISSUES_NEW_CHOOSE_URL,
    MD_NAME,
    MITMACHEN_INTRO,
    MITMACHEN_LINK_LABEL,
    REPO_INTRO,
    REPO_LINK_LABEL,
    REPO_URL,
    compile_timestamp,
    json_status_date,
    link_or_empty,
    load_entries,
    output_dir,
    sorted_by_episode,
)


def _cell(text: str | None) -> str:
    if text is None:
        return ""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def _md_link(label: str, url: str | None) -> str:
    if not url:
        return "—"
    return f"[{_cell(label)}]({url})"


def render_markdown(entries=None, *, compiled_at: str | None = None, json_date: str | None = None) -> str:
    if entries is None:
        entries = load_entries()
    entries = sorted_by_episode(entries)
    compiled_at = compiled_at or compile_timestamp()
    if json_date is None:
        json_date = json_status_date()
    json_line = json_date if json_date else "noch nicht gesetzt"

    lines = [
        "# GAG Metal Playlist: Metal-Song trifft GAG-Folge",
        "",
        f"<small>**Compile-Datum:** {compiled_at}  </small>",
        f"<small>**JSON-Status:** {json_line}  </small>",
        f"{REPO_INTRO} [{REPO_LINK_LABEL}]({REPO_URL}).",
        "",
        f"{MITMACHEN_INTRO} [{MITMACHEN_LINK_LABEL}]({ISSUES_NEW_CHOOSE_URL})",
        "",
        "**Stufe A** – Song und Folge behandeln denselben Kerngegenstand (Person/Ereignis/Ort im Fokus).  ",
        "**Stufe B** – gemeinsamer historischer Rahmen, klar anderer Fokus oder nur Inspiration/Metapher.",
        "",
        "| Folge | Folgentitel | Band | Song Titel | Stufe | YouTube | Spotify |",
        "| ---: | --- | --- | --- | :---: | :---: | :---: |",
    ]
    for e in entries:
        ep_id = e.get("episodeId")
        ep_label = str(ep_id) if ep_id is not None else "?"
        stufe = e.get("matchTier") or "—"
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_link(ep_label, link_or_empty(e.get("episodeUrl"))),
                    _cell(e.get("episodeTitle")),
                    _cell(e.get("band")),
                    _cell(e.get("songTitle")),
                    _cell(stufe),
                    _md_link("link", link_or_empty(e.get("youtubeUrl"))),
                    _md_link("link", link_or_empty(e.get("spotifyUrl"))),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_markdown(out_path: Path | None = None) -> Path:
    path = out_path or (output_dir() / MD_NAME)
    path.write_text(render_markdown(), encoding="utf-8")
    return path
