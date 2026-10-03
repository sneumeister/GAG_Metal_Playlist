# -*- coding: utf-8 -*-
"""Gemeinsame Hilfen für den Playlist-Export."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_NAME = "GAG_Metal_Playlist.json"
REJECTED_JSON_NAME = "rejected.json"
MD_NAME = "GAG_Metal_playlist.md"
HTML_NAME = "GAG_Metal_playlist.html"

# Repo / Mitmachen (für HTML- und Markdown-Export)
REPO_URL = "https://github.com/sneumeister/GAG_Metal_Playlist"
REPO_LINK_LABEL = "github.com/sneumeister/GAG_Metal_Playlist"
REPO_INTRO = "Original-Projekt, Hinweise und Quellen auf"
ISSUES_NEW_CHOOSE_URL = f"{REPO_URL}/issues/new/choose"
MITMACHEN_INTRO = (
    "Songvorschläge, Korrekturen und anderes Feedback: über GitHub Issues."
)
MITMACHEN_LINK_LABEL = "Neues Issue öffnen"


def data_dir() -> Path:
    """Verzeichnis der JSON-Quelle (gleicher Ordner wie die Export-Skripte)."""
    return Path(__file__).resolve().parent.parent


def output_dir() -> Path:
    """Projektverzeichnis: eine Ebene über `data/`."""
    return data_dir().parent


def file_updated_at() -> str:
    """Zeitstempel für Datei-`updatedAt` (Playlist, Rejects): YYYY-MM-DD HH:MM:SS ±ZZZZ."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def compile_timestamp() -> str:
    # Alias: Export-Compile-Datum nutzt dasselbe Format wie Datei-`updatedAt`.
    return file_updated_at()


def entries_from_raw(raw: Any, *, path_hint: str | Path = "JSON") -> list[dict[str, Any]]:
    """
    Extrahiert Einträge aus Playlist-/Reject-Dokumenten.
    Kanonisch: Objekt mit `entries`; nacktes Array nur als Fallback.
    """
    if isinstance(raw, dict) and "entries" in raw:
        return list(raw.get("entries") or [])
    if isinstance(raw, list):
        return list(raw)
    raise ValueError(f"Unerwartetes JSON-Format in {path_hint}")


def wrap_entries_document(
    entries: list[dict[str, Any]],
    *,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Objektform mit `updatedAt` + `entries` (Playlist / Rejects)."""
    return {
        "updatedAt": updated_at or file_updated_at(),
        "entries": list(entries),
    }


def load_entries(path: Path | None = None) -> list[dict[str, Any]]:
    """Liest Match-Einträge. Kanonisch: Objekt mit `entries`; Array nur als Fallback."""
    json_path = path or (data_dir() / JSON_NAME)
    raw = json.loads(json_path.read_text(encoding="utf-8-sig"))
    return entries_from_raw(raw, path_hint=json_path)


def load_rejected_entries(path: Path | None = None) -> list[dict[str, Any]]:
    """Liest Reject-Einträge. Kanonisch: Objekt mit `entries`; Array nur als Fallback."""
    json_path = path or (data_dir() / REJECTED_JSON_NAME)
    raw = json.loads(json_path.read_text(encoding="utf-8-sig"))
    return entries_from_raw(raw, path_hint=json_path)


def json_status_date(path: Path | None = None) -> str | None:
    """
    Letzter Bearbeitungszeitpunkt der Playlist-JSON (`updatedAt`).
    Erwartetes Format: YYYY-MM-DD HH:MM:SS ±ZZZZ (wie file_updated_at).
    Fallback: ältere Meta-Keys bzw. Neben-Datei `*.meta.json`.
    """
    json_path = path or (data_dir() / JSON_NAME)
    raw = json.loads(json_path.read_text(encoding="utf-8-sig"))
    if isinstance(raw, dict):
        for key in ("updatedAt", "generatedAt", "createdAt", "exportedAt"):
            if raw.get(key):
                return str(raw[key])
    meta_path = json_path.with_suffix(".meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        for key in ("updatedAt", "generatedAt", "createdAt", "exportedAt"):
            if meta.get(key):
                return str(meta[key])
    return None


def sorted_by_episode(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda e: (e.get("episodeId") is None, e.get("episodeId", 0), e.get("songTitle") or ""))


def link_or_empty(url: str | None) -> str | None:
    if url and str(url).strip() and str(url).lower() != "null":
        return str(url).strip()
    return None
