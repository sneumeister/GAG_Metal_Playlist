# -*- coding: utf-8 -*-
"""
Episoden-Snapshot mit Upstream abgleichen (Datums-Gate, ID-Mengen-Diff).

Vergleicht `fetchedAt` in data/episodes.meta.json mit dem letzten Commit-Datum
der Upstream-Datei. Nur wenn Remote jünger ist, wird heruntergeladen.

Lokale Zeilen, die Upstream noch fehlen, bleiben erhalten. Dieselbe id mit
anderem checksum gilt als Korrektur und löst keinen Match-Lauf aus.

Aufruf:
  python scripts/sync_episodes.py
  python scripts/sync_episodes.py --check
  python scripts/sync_episodes.py --force

Exit-Codes:
  0  Snapshot aktualisiert (Download + Merge geschrieben)
  2  nichts zu tun (Remote nicht jünger, oder --check ohne Schreibbedarf)
  1  Fehler
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EPISODES_PATH = DATA / "episodes.jsonl"
META_PATH = DATA / "episodes.meta.json"

DEFAULT_SOURCE_URL = (
    "https://raw.githubusercontent.com/ideadapt/"
    "geschichten-aus-der-geschichte-data/refs/heads/main/data/episodes.jsonl"
)
COMMITS_API_URL = (
    "https://api.github.com/repos/ideadapt/geschichten-aus-der-geschichte-data"
    "/commits?path=data/episodes.jsonl&per_page=1"
)
USER_AGENT = "GAG-Metal-Playlist-sync_episodes/1.0"


def parse_iso(value: str) -> datetime:
    """ISO-8601 mit optionalem Z in aware UTC-Datetime."""
    text = (value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_remote_commit_date() -> datetime:
    raw = http_get(COMMITS_API_URL)
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("GitHub-Commits-API lieferte keinen Commit für episodes.jsonl")
    date_str = payload[0]["commit"]["committer"]["date"]
    return parse_iso(date_str)


def load_meta() -> dict[str, Any]:
    if not META_PATH.exists():
        return {
            "lineCount": 0,
            "fetchedAt": "1970-01-01T00:00:00Z",
            "sourceUrl": DEFAULT_SOURCE_URL,
        }
    return json.loads(META_PATH.read_text(encoding="utf-8-sig"))


def load_episodes_by_id(text: str) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        ep = json.loads(line)
        eid = ep.get("id")
        if eid is None:
            continue
        out[int(eid)] = ep
    return out


def load_local_episodes() -> dict[int, dict[str, Any]]:
    if not EPISODES_PATH.exists():
        return {}
    return load_episodes_by_id(EPISODES_PATH.read_text(encoding="utf-8-sig"))


def write_episodes(by_id: dict[int, dict[str, Any]]) -> None:
    lines = [
        json.dumps(by_id[eid], ensure_ascii=False, separators=(",", ":"))
        for eid in sorted(by_id)
    ]
    EPISODES_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_meta(meta: dict[str, Any]) -> None:
    META_PATH.write_text(
        json.dumps(meta, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )


def merge_episodes(
    local: dict[int, dict[str, Any]],
    remote: dict[int, dict[str, Any]],
) -> tuple[dict[int, dict[str, Any]], list[int], list[int], list[int]]:
    """
    Remote übernehmen, lokale Extra-IDs behalten.
    Returns: merged, new_ids, checksum_changed_ids, local_only_ids
    """
    merged = dict(local)
    new_ids: list[int] = []
    checksum_changed: list[int] = []

    for eid, rep in remote.items():
        if eid not in local:
            merged[eid] = rep
            new_ids.append(eid)
            continue
        old = local[eid]
        if old.get("checksum") != rep.get("checksum"):
            checksum_changed.append(eid)
        merged[eid] = rep

    local_only = sorted(set(local) - set(remote))
    new_ids.sort()
    checksum_changed.sort()
    return merged, new_ids, checksum_changed, local_only


def build_note(local_only: list[int]) -> str | None:
    if not local_only:
        return None
    ids = ", ".join(str(i) for i in local_only)
    return (
        f"Episode(n) {ids} lokal ergänzt "
        f"(Upstream noch ohne diese Nummer(n))."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Episoden-Snapshot mit Upstream abgleichen (Datums-Gate)."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nur prüfen und melden, nichts schreiben",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download auch wenn Remote nicht jünger als fetchedAt",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ergebnis als JSON auf stdout",
    )
    args = parser.parse_args()

    try:
        meta = load_meta()
        local_fetched = parse_iso(str(meta.get("fetchedAt") or "1970-01-01T00:00:00Z"))
        remote_date = fetch_remote_commit_date()
        source_url = str(meta.get("sourceUrl") or DEFAULT_SOURCE_URL)

        result: dict[str, Any] = {
            "status": "up_to_date",
            "localFetchedAt": local_fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "remoteCommitAt": remote_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "newEpisodeIds": [],
            "checksumChangedIds": [],
            "localOnlyIds": [],
            "lineCount": int(meta.get("lineCount") or 0),
            "wrote": False,
        }

        remote_newer = remote_date > local_fetched
        if not remote_newer and not args.force:
            msg = (
                f"Nichts zu tun: Remote-Commit {result['remoteCommitAt']} "
                f"ist nicht juenger als fetchedAt {result['localFetchedAt']}."
            )
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(msg)
            return 2

        # Remote juenger (oder --force): Inhalt laden, Diff berechnen
        remote_text = http_get(source_url).decode("utf-8")
        local = load_local_episodes()
        remote = load_episodes_by_id(remote_text)
        merged, new_ids, checksum_changed, local_only = merge_episodes(local, remote)

        result["newEpisodeIds"] = new_ids
        result["checksumChangedIds"] = checksum_changed
        result["localOnlyIds"] = local_only
        result["lineCount"] = len(merged)

        if args.check:
            result["status"] = "would_update"
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(
                    f"Wuerde aktualisieren: neu={new_ids or '-'}; "
                    f"checksum={checksum_changed or '-'}; "
                    f"nur-lokal={local_only or '-'}; Zeilen={len(merged)}"
                )
            return 2

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_episodes(merged)
        new_meta: dict[str, Any] = {
            "lineCount": len(merged),
            "fetchedAt": now,
            "sourceUrl": source_url,
        }
        note = build_note(local_only)
        if note:
            new_meta["note"] = note
        write_meta(new_meta)

        result["status"] = "updated"
        result["wrote"] = True
        result["localFetchedAt"] = now

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(
                f"Snapshot aktualisiert: neu={new_ids or '-'}; "
                f"checksum-Korrekturen={checksum_changed or '-'}; "
                f"nur-lokal behalten={local_only or '-'}; "
                f"Zeilen={len(merged)}; fetchedAt={now}"
            )
            if new_ids:
                print(
                    "Neue Folgennummern (fuer collect_candidates): "
                    + ",".join(str(i) for i in new_ids)
                )
            else:
                print("Keine neuen Folgennummern - kein Match-Lauf noetig.")
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError, RuntimeError, json.JSONDecodeError, KeyError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
