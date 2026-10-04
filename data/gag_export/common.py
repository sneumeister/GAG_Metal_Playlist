# -*- coding: utf-8 -*-
"""Gemeinsame Hilfen für den Playlist-Export."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_NAME = "GAG_Metal_Playlist.json"
REJECTED_JSON_NAME = "rejected.json"
SONGS_JSON_NAME = "songs.json"
EPISODES_JSONL_NAME = "episodes.jsonl"
MD_NAME = "GAG_Metal_playlist.md"
HTML_NAME = "GAG_Metal_playlist.html"
REJECT_MD_NAME = "GAG_Metal_rejected.md"
REJECT_HTML_NAME = "GAG_Metal_rejected.html"

# Repo / Mitmachen (für HTML- und Markdown-Export)
REPO_URL = "https://github.com/sneumeister/GAG_Metal_Playlist"
REPO_LINK_LABEL = "github.com/sneumeister/GAG_Metal_Playlist"
REPO_INTRO = "Original-Projekt, Hinweise und Quellen auf"
ISSUES_NEW_CHOOSE_URL = f"{REPO_URL}/issues/new/choose"
MITMACHEN_INTRO = (
    "Songvorschläge, Korrekturen und anderes Feedback: über GitHub Issues."
)
MITMACHEN_LINK_LABEL = "Neues Issue öffnen"

# Gegenseitige Verweise Playlist ↔ Reject-Liste
CROSSLINK_TO_REJECTS_INTRO = "Geprüfte Absagen (Stufe X):"
CROSSLINK_TO_PLAYLIST_INTRO = "Trefferliste (Stufen A/B/C):"


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


def load_songs_by_id(path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Song-Katalog als `songId` → Eintrag."""
    json_path = path or (data_dir() / SONGS_JSON_NAME)
    raw = json.loads(json_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, list):
        raise ValueError(f"Unerwartetes songs.json-Format in {json_path}")
    return {str(s["id"]): s for s in raw if s.get("id")}


def load_episodes_by_id(path: Path | None = None) -> dict[int, dict[str, Any]]:
    """Folien-Snapshot als `episodeId` → Eintrag."""
    jsonl_path = path or (data_dir() / EPISODES_JSONL_NAME)
    out: dict[int, dict[str, Any]] = {}
    if not jsonl_path.exists():
        return out
    for line in jsonl_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        eid = e.get("id")
        if eid is not None:
            out[int(eid)] = e
    return out


def enrich_rejected_entries(
    entries: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Reject-Rohdaten um Band/Titel/Links/Folgentitel anreichern
    (Export-Format analog zur Playlist-Zeile, Stufe immer X).
    """
    if entries is None:
        entries = load_rejected_entries()
    songs = load_songs_by_id()
    episodes = load_episodes_by_id()
    enriched: list[dict[str, Any]] = []
    for e in entries:
        song_id = e.get("songId") or ""
        song = songs.get(str(song_id), {})
        eid = e.get("episodeId")
        ep = episodes.get(int(eid), {}) if eid is not None else {}
        ep_url = link_or_empty(ep.get("websiteUrl")) or (
            f"https://gadg.fm/{eid}" if eid is not None else None
        )
        enriched.append(
            {
                "episodeId": eid,
                "episodeTitle": ep.get("title") or "",
                "episodeUrl": ep_url,
                "songId": song_id,
                "band": song.get("band") or "",
                "songTitle": song.get("title") or song_id,
                "matchTier": "X",
                "justification": e.get("reason") or "",
                "youtubeUrl": song.get("youtubeUrl"),
                "spotifyUrl": song.get("spotifyUrl"),
                "rejectedAt": e.get("rejectedAt"),
                "rejectedBy": e.get("rejectedBy"),
            }
        )
    return enriched


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
