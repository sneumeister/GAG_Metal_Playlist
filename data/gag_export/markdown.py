# -*- coding: utf-8 -*-
"""Markdown-Export der GAG Metal Playlist und Reject-Liste."""
from __future__ import annotations

from pathlib import Path

from .common import (
    CROSSLINK_TO_PLAYLIST_INTRO,
    CROSSLINK_TO_REJECTS_INTRO,
    ISSUES_NEW_CHOOSE_URL,
    MD_NAME,
    MITMACHEN_INTRO,
    MITMACHEN_LINK_LABEL,
    REJECT_MD_NAME,
    REJECTED_JSON_NAME,
    REPO_INTRO,
    REPO_LINK_LABEL,
    REPO_URL,
    compile_timestamp,
    data_dir,
    enrich_rejected_entries,
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


def _table_rows(entries: list) -> list[str]:
    lines = []
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
    return lines


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
        f"{CROSSLINK_TO_REJECTS_INTRO} [{REJECT_MD_NAME}]({REJECT_MD_NAME})",
        "",
        "**Stufe A** – Song und Folge behandeln denselben Kerngegenstand (Person/Ereignis/Ort im Fokus).  ",
        "**Stufe B** – gemeinsamer historischer Rahmen mit klarer Überschneidung, aber klar anderem Fokus.  ",
        "**Stufe C** – erkennbare thematische/assoziative Nähe ohne gemeinsamen Erzählgegenstand; auch reine Inspiration/Metapher.",
        "",
        "| Folge | Folgentitel | Band | Song Titel | Stufe | YouTube | Spotify |",
        "| ---: | --- | --- | --- | :---: | :---: | :---: |",
    ]
    lines.extend(_table_rows(entries))
    lines.append("")
    return "\n".join(lines)


def render_rejected_markdown(
    entries=None, *, compiled_at: str | None = None, json_date: str | None = None
) -> str:
    if entries is None:
        entries = enrich_rejected_entries()
    entries = sorted_by_episode(entries)
    compiled_at = compiled_at or compile_timestamp()
    if json_date is None:
        json_date = json_status_date(data_dir() / REJECTED_JSON_NAME)
    json_line = json_date if json_date else "noch nicht gesetzt"

    lines = [
        "# GAG Metal Rejects: Geprüfte Absagen (Stufe X)",
        "",
        f"<small>**Compile-Datum:** {compiled_at}  </small>",
        f"<small>**JSON-Status:** {json_line}  </small>",
        f"{REPO_INTRO} [{REPO_LINK_LABEL}]({REPO_URL}).",
        "",
        f"{MITMACHEN_INTRO} [{MITMACHEN_LINK_LABEL}]({ISSUES_NEW_CHOOSE_URL})",
        "",
        f"{CROSSLINK_TO_PLAYLIST_INTRO} [{MD_NAME}]({MD_NAME})",
        "",
        "**Stufe X** – kein brauchbarer Bezug (falsche Person/Phase/Ereignis, reiner Namens-/Zahlenanklang, Genre-Fail, …).  ",
        "Diese Paare wurden geprüft und bewusst nicht in die Playlist aufgenommen.",
        "",
        "| Folge | Folgentitel | Band | Song Titel | Stufe | YouTube | Spotify |",
        "| ---: | --- | --- | --- | :---: | :---: | :---: |",
    ]
    lines.extend(_table_rows(entries))
    lines.append("")
    return "\n".join(lines)


def write_markdown(out_path: Path | None = None) -> Path:
    path = out_path or (output_dir() / MD_NAME)
    path.write_text(render_markdown(), encoding="utf-8")
    return path


def write_rejected_markdown(out_path: Path | None = None) -> Path:
    path = out_path or (output_dir() / REJECT_MD_NAME)
    path.write_text(render_rejected_markdown(), encoding="utf-8")
    return path
