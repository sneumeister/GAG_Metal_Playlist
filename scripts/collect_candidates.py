# -*- coding: utf-8 -*-
"""
Offene Kandidaten-Paare in scripts/_tmp_round.json sammeln (ohne Stufe).

Eingaben:
  - neue Folgennummern (nach sync_episodes): Abgleich gegen songs.json
  - einzelnes Paar (Issue/manuell/Web): Band + Titel + Folge

Paare, die schon in der Playlist oder in rejected.json stehen, werden
übersprungen. proposedTier und justification bleiben leer, bis die
Deep-Analysis sie füllt.

Aufruf:
  python scripts/collect_candidates.py --episodes 577,578
  python scripts/collect_candidates.py --band Sabaton --title "The Last Stand" --folge 157 --source issue
  python scripts/collect_candidates.py --song-id sabaton-the-last-stand --folge 157 --source search
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
QUEUE_PATH = ROOT / "scripts" / "_tmp_round.json"

if str(DATA) not in sys.path:
    sys.path.insert(0, str(DATA))

from gag_export.common import entries_from_raw  # noqa: E402

VALID_SOURCES = ("issue", "new-episode", "search", "manual", "web")
MIN_ENTITY_LEN = 3


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_episodes_by_id() -> dict[int, dict[str, Any]]:
    path = DATA / "episodes.jsonl"
    out: dict[int, dict[str, Any]] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        ep = json.loads(line)
        eid = ep.get("id")
        if eid is not None:
            out[int(eid)] = ep
    return out


def decided_pairs() -> set[tuple[int, str]]:
    playlist = entries_from_raw(
        load_json(DATA / "GAG_Metal_Playlist.json", {"entries": []}),
        path_hint="GAG_Metal_Playlist.json",
    )
    rejected = entries_from_raw(
        load_json(DATA / "rejected.json", {"entries": []}),
        path_hint="rejected.json",
    )
    out: set[tuple[int, str]] = set()
    for row in playlist + rejected:
        eid = row.get("episodeId")
        sid = row.get("songId")
        if eid is None or not sid:
            continue
        out.add((int(eid), str(sid)))
    return out


def load_queue() -> dict[str, Any]:
    raw = load_json(QUEUE_PATH, None)
    if raw is None:
        return {"updatedAt": now_stamp(), "entries": []}
    if isinstance(raw, list):
        return {"updatedAt": now_stamp(), "entries": list(raw)}
    if isinstance(raw, dict):
        entries = list(raw.get("entries") or [])
        return {"updatedAt": raw.get("updatedAt") or now_stamp(), "entries": entries}
    raise ValueError(f"Unerwartetes Queue-Format in {QUEUE_PATH}")


def queue_open_keys(entries: list[dict[str, Any]]) -> set[tuple[int, str]]:
    keys: set[tuple[int, str]] = set()
    for row in entries:
        if row.get("status") not in (None, "open"):
            continue
        eid = row.get("episodeId")
        sid = row.get("songId")
        if eid is None or not sid:
            # Band/Titel ohne songId: eigener Schlüssel
            band = normalize(str(row.get("band") or ""))
            title = normalize(str(row.get("title") or ""))
            if eid is not None and band and title:
                keys.add((int(eid), f"pending:{band}|{title}"))
            continue
        keys.add((int(eid), str(sid)))
    return keys


def episode_blob(ep: dict[str, Any]) -> str:
    parts = [
        str(ep.get("title") or ""),
        str(ep.get("description") or ""),
    ]
    for loc in ep.get("locations") or []:
        if isinstance(loc, dict):
            parts.append(str(loc.get("name") or loc.get("label") or ""))
        else:
            parts.append(str(loc))
    for link in ep.get("temporalLinks") or []:
        if isinstance(link, dict):
            parts.append(str(link.get("label") or link.get("name") or ""))
        else:
            parts.append(str(link))
    return normalize(" ".join(parts))


def entity_hits(blob: str, entities: list[str]) -> list[str]:
    hits: list[str] = []
    for ent in entities:
        ent_s = str(ent or "").strip()
        if len(ent_s) < MIN_ENTITY_LEN:
            continue
        needle = normalize(ent_s)
        if not needle:
            continue
        # Wortgrenzen grob: Leerzeichen oder Ränder
        if re.search(rf"(?:^|\s){re.escape(needle)}(?:\s|$)", blob):
            hits.append(ent_s)
    return hits


def empty_entry(
    *,
    source: str,
    episode_id: int,
    song_id: str | None = None,
    band: str | None = None,
    title: str | None = None,
    issue_url: str | None = None,
    submitter_note: str | None = None,
    matched_entities: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source": source,
        "episodeId": episode_id,
        "songId": song_id,
        "band": band,
        "title": title,
        "issueUrl": issue_url,
        "submitterNote": submitter_note,
        "matchedEntities": matched_entities or [],
        "status": "open",
        "proposedTier": None,
        "justification": None,
    }


def parse_episode_ids(text: str) -> list[int]:
    ids: list[int] = []
    for part in re.split(r"[,\s]+", text.strip()):
        if not part:
            continue
        ids.append(int(part))
    return sorted(set(ids))


def songs_by_id() -> dict[str, dict[str, Any]]:
    raw = load_json(DATA / "songs.json", [])
    if not isinstance(raw, list):
        raise ValueError("songs.json muss ein Array sein")
    return {str(s["id"]): s for s in raw if s.get("id")}


def find_song(band: str, title: str, catalog: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    nb = normalize(band)
    nt = normalize(title)
    for song in catalog.values():
        if normalize(str(song.get("band") or "")) == nb and normalize(
            str(song.get("title") or "")
        ) == nt:
            return song
    return None


def collect_for_episodes(
    episode_ids: list[int],
    *,
    source: str,
) -> list[dict[str, Any]]:
    eps = load_episodes_by_id()
    catalog = songs_by_id()
    decided = decided_pairs()
    missing = [eid for eid in episode_ids if eid not in eps]
    if missing:
        raise ValueError(f"Folgen nicht im Snapshot: {', '.join(str(i) for i in missing)}")

    candidates: list[dict[str, Any]] = []
    for eid in episode_ids:
        blob = episode_blob(eps[eid])
        for song in catalog.values():
            sid = str(song["id"])
            if (eid, sid) in decided:
                continue
            hits = entity_hits(blob, list(song.get("entities") or []))
            if not hits:
                continue
            candidates.append(
                empty_entry(
                    source=source,
                    episode_id=eid,
                    song_id=sid,
                    band=str(song.get("band") or ""),
                    title=str(song.get("title") or ""),
                    matched_entities=hits,
                )
            )
    return candidates


def collect_pair(
    *,
    episode_id: int,
    source: str,
    song_id: str | None,
    band: str | None,
    title: str | None,
    issue_url: str | None,
    submitter_note: str | None,
) -> dict[str, Any]:
    eps = load_episodes_by_id()
    if episode_id not in eps:
        raise ValueError(f"Folge #{episode_id} nicht im Snapshot")

    catalog = songs_by_id()
    decided = decided_pairs()
    song: dict[str, Any] | None = None
    if song_id:
        song = catalog.get(song_id)
        if song is None:
            raise ValueError(f"songId nicht im Katalog: {song_id}")
    elif band and title:
        song = find_song(band, title, catalog)

    if song:
        sid = str(song["id"])
        if (episode_id, sid) in decided:
            raise ValueError(
                f"Paar schon entschieden: Folge #{episode_id} / {sid} "
                f"(Playlist oder rejected)"
            )
        return empty_entry(
            source=source,
            episode_id=episode_id,
            song_id=sid,
            band=str(song.get("band") or band or ""),
            title=str(song.get("title") or title or ""),
            issue_url=issue_url,
            submitter_note=submitter_note,
        )

    if not band or not title:
        raise ValueError("Ohne Katalog-Treffer bitte --band und --title angeben")

    return empty_entry(
        source=source,
        episode_id=episode_id,
        song_id=None,
        band=band,
        title=title,
        issue_url=issue_url,
        submitter_note=submitter_note,
    )


def append_entries(new_entries: list[dict[str, Any]]) -> tuple[int, int]:
    queue = load_queue()
    entries = list(queue.get("entries") or [])
    open_keys = queue_open_keys(entries)
    added = 0
    skipped = 0
    for row in new_entries:
        eid = int(row["episodeId"])
        sid = row.get("songId")
        if sid:
            key = (eid, str(sid))
        else:
            key = (
                eid,
                f"pending:{normalize(str(row.get('band') or ''))}|{normalize(str(row.get('title') or ''))}",
            )
        if key in open_keys:
            skipped += 1
            continue
        entries.append(row)
        open_keys.add(key)
        added += 1
    if added == 0 and not QUEUE_PATH.exists():
        return added, skipped
    if added == 0 and not entries:
        return added, skipped
    queue["entries"] = entries
    queue["updatedAt"] = now_stamp()
    save_json(QUEUE_PATH, queue)
    return added, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offene Kandidaten nach scripts/_tmp_round.json schreiben."
    )
    parser.add_argument(
        "--episodes",
        help="Komma-/leerseparierte Folgennummern (Entity-Abgleich gegen songs.json)",
    )
    parser.add_argument("--folge", type=int, help="Einzelne Folgennummer (Paar-Modus)")
    parser.add_argument("--song-id", help="Song-ID aus songs.json")
    parser.add_argument("--band", help="Band (Paar-Modus)")
    parser.add_argument("--title", help="Songtitel (Paar-Modus)")
    parser.add_argument(
        "--source",
        choices=VALID_SOURCES,
        help="Quelle des Eintrags (Default: new-episode bzw. manual)",
    )
    parser.add_argument("--issue-url", help="Issue-URL (optional)")
    parser.add_argument("--note", help="Einreicher-/Notiztext (optional)")
    args = parser.parse_args()

    if args.episodes and (args.folge or args.song_id or args.band or args.title):
        print("Entweder --episodes oder Paar-Modus (--folge …), nicht beides.", file=sys.stderr)
        return 1

    try:
        if args.episodes:
            source = args.source or "new-episode"
            ids = parse_episode_ids(args.episodes)
            if not ids:
                print("Keine Folgennummern übergeben.", file=sys.stderr)
                return 1
            new_entries = collect_for_episodes(ids, source=source)
        elif args.folge is not None:
            source = args.source or "manual"
            if not args.song_id and not (args.band and args.title):
                print("Paar-Modus braucht --song-id oder --band und --title.", file=sys.stderr)
                return 1
            new_entries = [
                collect_pair(
                    episode_id=args.folge,
                    source=source,
                    song_id=args.song_id,
                    band=args.band,
                    title=args.title,
                    issue_url=args.issue_url,
                    submitter_note=args.note,
                )
            ]
        else:
            print("Bitte --episodes … oder --folge … angeben.", file=sys.stderr)
            return 1

        added, skipped = append_entries(new_entries)
        open_count = sum(
            1
            for e in load_queue().get("entries") or []
            if e.get("status") in (None, "open")
        )
        print(
            f"Queue {QUEUE_PATH.relative_to(ROOT)}: "
            f"+{added} neu, {skipped} schon offen uebersprungen, "
            f"{open_count} offen gesamt "
            f"(Kandidaten dieses Laufs vor Filter: {len(new_entries)})."
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
