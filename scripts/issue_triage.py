# -*- coding: utf-8 -*-
"""
Prüft Playlist-Vorschlag-Issues gegen Katalog, Matches und Rejects.

Liest Band / Songtitel / GAG-Folge aus dem GitHub-Issue-Formular und schreibt
einen Markdown-Kommentar (Tipp für die Kuratierung).

Aufruf:
  python scripts/issue_triage.py --body-file body.md --comment-file comment.md
  python scripts/issue_triage.py --band Sabaton --title Father --folge 157
  echo "$ISSUE_BODY" | python scripts/issue_triage.py --comment-file comment.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
if str(DATA) not in sys.path:
    sys.path.insert(0, str(DATA))

from gag_export.common import entries_from_raw  # noqa: E402

EMPTY_MARKERS = {"", "_no response_", "n/a", "none", "-", "–"}

# GitHub-Issue-Form: ### Label\n\nWert
FORM_SECTION_RE = re.compile(
    r"^###\s+(.+?)\s*\n+([\s\S]*?)(?=^###\s+|\Z)",
    re.MULTILINE,
)
EPISODE_NUM_RE = re.compile(r"\b(\d{1,4})\b")


def normalize(text: str) -> str:
    """Vergleichsnormalisierung: Kleinbuchstaben, ohne Akzente/Satzzeichen."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def is_empty(value: str | None) -> bool:
    return normalize(value or "") in EMPTY_MARKERS or not (value or "").strip()


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_episodes(path: Path) -> dict[int, dict]:
    episodes: dict[int, dict] = {}
    if not path.exists():
        return episodes
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ep = json.loads(line)
            episodes[int(ep["id"])] = ep
    return episodes


def parse_issue_form(body: str) -> dict[str, str]:
    """Extrahiert Abschnitte aus einem GitHub-Issue-Formular-Body."""
    body = (body or "").lstrip("\ufeff")
    fields: dict[str, str] = {}
    for match in FORM_SECTION_RE.finditer(body):
        label = match.group(1).strip()
        value = match.group(2).strip()
        fields[label] = value
    return fields


def form_get(fields: dict[str, str], *labels: str) -> str:
    by_norm = {normalize(k): v for k, v in fields.items()}
    for label in labels:
        key = normalize(label)
        if key in by_norm and not is_empty(by_norm[key]):
            return by_norm[key].strip()
    return ""


@dataclass
class SongHit:
    song_id: str
    band: str
    title: str
    how: str  # exact | band+title-fuzzy | playlist-direct


@dataclass
class TriageResult:
    band: str = ""
    title: str = ""
    folge_raw: str = ""
    episode_id: int | None = None
    episode_title: str | None = None
    songs: list[SongHit] = field(default_factory=list)
    playlist_hits: list[dict] = field(default_factory=list)
    reject_hits: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)


def resolve_episode(
    folge_raw: str,
    episodes: dict[int, dict],
    playlist_entries: list[dict],
) -> tuple[int | None, str | None, list[str]]:
    notes: list[str] = []
    if is_empty(folge_raw):
        return None, None, ["Keine GAG-Folge angegeben."]

    # Explizite Nummer bevorzugt (erste sinnvolle Zahl)
    nums = [int(n) for n in EPISODE_NUM_RE.findall(folge_raw)]
    for num in nums:
        if num in episodes:
            return num, episodes[num].get("title"), []
        # auch in Playlist-Einträgen (falls Snapshot älter)
        for entry in playlist_entries:
            if entry.get("episodeId") == num:
                return num, entry.get("episodeTitle"), [
                    f"Folge {num} nicht in episodes.jsonl, Titel aus Playlist."
                ]

    # Titel-Suche
    needle = normalize(folge_raw)
    # Zahlen-only Strings ohne Treffer → Hinweis
    if nums and needle == normalize(str(nums[0])):
        return None, None, [f"Folge {nums[0]} nicht gefunden."]

    candidates: list[tuple[int, str, int]] = []
    for eid, ep in episodes.items():
        title = ep.get("title") or ""
        nt = normalize(title)
        if not nt:
            continue
        if needle == nt or needle in nt or nt in needle:
            # kürzere Titel-Differenz = besserer Treffer
            score = abs(len(nt) - len(needle))
            candidates.append((score, eid, title))

    if not candidates:
        # Playlist-Titel als Fallback
        for entry in playlist_entries:
            title = entry.get("episodeTitle") or ""
            nt = normalize(title)
            if nt and (needle == nt or needle in nt or nt in needle):
                eid = int(entry["episodeId"])
                candidates.append((abs(len(nt) - len(needle)), eid, title))

    if not candidates:
        return None, None, [f"Folge nicht eindeutig zuordenbar: „{folge_raw.strip()}“."]

    candidates.sort()
    best_score, eid, title = candidates[0]
    if len(candidates) > 1 and candidates[1][0] == best_score:
        alts = ", ".join(f"{c[1]} ({c[2]})" for c in candidates[:5])
        notes.append(f"Mehrere Folgen-Kandidaten: {alts}. Nehme {eid}.")
    return eid, title, notes


def find_songs(
    band: str,
    title: str,
    songs: list[dict],
    playlist_entries: list[dict],
) -> list[SongHit]:
    nb, nt = normalize(band), normalize(title)
    if not nb and not nt:
        return []

    hits: list[SongHit] = []
    seen: set[str] = set()

    def add(song_id: str, b: str, t: str, how: str) -> None:
        if song_id in seen:
            return
        seen.add(song_id)
        hits.append(SongHit(song_id=song_id, band=b, title=t, how=how))

    for song in songs:
        sb, st = normalize(song.get("band", "")), normalize(song.get("title", ""))
        if nb and nt and sb == nb and st == nt:
            add(song["id"], song["band"], song["title"], "exact")
        elif nb and nt and sb == nb and (nt in st or st in nt):
            add(song["id"], song["band"], song["title"], "band+title-fuzzy")
        elif nb and not nt and sb == nb:
            add(song["id"], song["band"], song["title"], "band-only")
        elif nt and not nb and st == nt:
            add(song["id"], song["band"], song["title"], "title-only")

    # Playlist-Direktabgleich (falls Katalog-Lücke)
    for entry in playlist_entries:
        sb, st = normalize(entry.get("band", "")), normalize(entry.get("songTitle", ""))
        sid = entry.get("songId") or ""
        if not sid:
            continue
        if nb and nt and sb == nb and st == nt:
            add(sid, entry["band"], entry["songTitle"], "playlist-direct")
        elif nb and nt and sb == nb and (nt in st or st in nt):
            add(sid, entry["band"], entry["songTitle"], "playlist-direct-fuzzy")

    # exact zuerst
    order = {
        "exact": 0,
        "playlist-direct": 1,
        "band+title-fuzzy": 2,
        "playlist-direct-fuzzy": 3,
        "band-only": 4,
        "title-only": 5,
    }
    hits.sort(key=lambda h: (order.get(h.how, 9), h.song_id))
    return hits


def triage(
    band: str,
    title: str,
    folge_raw: str,
    *,
    data_dir: Path = DATA,
) -> TriageResult:
    songs = load_json(data_dir / "songs.json")
    playlist = load_json(data_dir / "GAG_Metal_Playlist.json")
    rejected_raw = load_json(data_dir / "rejected.json")
    episodes = load_episodes(data_dir / "episodes.jsonl")
    entries: list[dict] = entries_from_raw(playlist, path_hint=data_dir / "GAG_Metal_Playlist.json")
    rejected: list[dict] = entries_from_raw(rejected_raw, path_hint=data_dir / "rejected.json")

    result = TriageResult(band=band.strip(), title=title.strip(), folge_raw=folge_raw.strip())

    if is_empty(band) or is_empty(title):
        result.notes.append("Band und/oder Songtitel fehlen im Issue-Formular.")
        result.labels.append("triage-unparseable")
        return result

    eid, etitle, ep_notes = resolve_episode(folge_raw, episodes, entries)
    result.episode_id = eid
    result.episode_title = etitle
    result.notes.extend(ep_notes)

    result.songs = find_songs(band, title, songs, entries)
    song_ids = {h.song_id for h in result.songs}

    # Playlist-Treffer
    for entry in entries:
        sid = entry.get("songId")
        if sid not in song_ids:
            continue
        if eid is not None and entry.get("episodeId") != eid:
            # anderen Folgen-Match trotzdem merken, aber markieren
            result.playlist_hits.append({**entry, "_otherEpisode": True})
        else:
            result.playlist_hits.append({**entry, "_otherEpisode": False})

    # Reject-Treffer
    song_by_id = {s["id"]: s for s in songs}
    for rej in rejected:
        sid = rej.get("songId")
        if sid not in song_ids:
            continue
        if eid is not None and rej.get("episodeId") != eid:
            result.reject_hits.append({**rej, "_otherEpisode": True, "_song": song_by_id.get(sid)})
        else:
            result.reject_hits.append({**rej, "_otherEpisode": False, "_song": song_by_id.get(sid)})

    # Labels
    same_pl = [h for h in result.playlist_hits if not h.get("_otherEpisode")]
    same_rej = [h for h in result.reject_hits if not h.get("_otherEpisode")]
    if not result.songs:
        result.labels.append("triage-unknown")
    elif same_rej:
        result.labels.append("triage-rejected")
    elif same_pl:
        result.labels.append("triage-matched")
    else:
        result.labels.append("triage-new")

    return result


def format_comment(result: TriageResult) -> str:
    lines: list[str] = [
        "## Auto-Triage (Katalog / Playlist / Rejects)",
        "",
        "_Automatischer Abgleich – keine redaktionelle A/B-Entscheidung._",
        "",
    ]

    vorgeschlagen = f"**{result.band}** – **{result.title}**"
    if result.folge_raw:
        vorgeschlagen += f" / Folge „{result.folge_raw}“"
    lines.append(f"Vorschlag: {vorgeschlagen}")
    if result.episode_id is not None:
        et = result.episode_title or "?"
        lines.append(f"Aufgelöst als Folge **{result.episode_id}**: {et}")
    lines.append("")

    if result.notes:
        for note in result.notes:
            lines.append(f"- Hinweis: {note}")
        lines.append("")

    if not result.songs:
        lines.extend(
            [
                "### Katalog",
                "",
                "Song **nicht** in `data/songs.json` gefunden "
                "(Schreibweise prüfen oder neuer Katalog-Eintrag nötig).",
                "",
            ]
        )
    else:
        lines.extend(["### Katalog", ""])
        for hit in result.songs[:8]:
            lines.append(
                f"- `{hit.song_id}` — {hit.band} – {hit.title} _({hit.how})_"
            )
        if len(result.songs) > 8:
            lines.append(f"- … und {len(result.songs) - 8} weitere")
        lines.append("")

    same_pl = [h for h in result.playlist_hits if not h.get("_otherEpisode")]
    other_pl = [h for h in result.playlist_hits if h.get("_otherEpisode")]
    same_rej = [h for h in result.reject_hits if not h.get("_otherEpisode")]
    other_rej = [h for h in result.reject_hits if h.get("_otherEpisode")]

    lines.extend(["### Playlist (`GAG_Metal_Playlist.json`)", ""])
    if same_pl:
        for h in same_pl:
            tier = h.get("matchTier", "?")
            just = (h.get("justification") or "").strip()
            if len(just) > 280:
                just = just[:277] + "…"
            lines.append(
                f"- **Bereits Match** Folge {h.get('episodeId')} "
                f"({h.get('band')} – {h.get('songTitle')}), Tier {tier}."
            )
            if just:
                lines.append(f"  - {just}")
    elif result.songs and result.episode_id is not None:
        lines.append(
            "- Kein bestehender Match für diesen Song **mit dieser Folge**."
        )
    elif result.songs:
        lines.append(
            "- Kein Abgleich auf Folgen-Ebene möglich (Folge unklar)."
        )
    else:
        lines.append("- Kein Abgleich (Song unbekannt).")

    if other_pl:
        lines.append("")
        lines.append("Andere Folgen mit diesem Song:")
        for h in other_pl[:6]:
            lines.append(
                f"- Folge {h.get('episodeId')} ({h.get('episodeTitle')}), "
                f"Tier {h.get('matchTier', '?')}"
            )
    lines.append("")

    lines.extend(["### Rejects (`rejected.json`)", ""])
    if same_rej:
        for h in same_rej:
            reason = (h.get("reason") or "").strip()
            lines.append(
                f"- **Bereits abgelehnt** für Folge {h.get('episodeId')} "
                f"(`{h.get('songId')}`)."
            )
            if reason:
                lines.append(f"  - {reason}")
    elif result.songs and result.episode_id is not None:
        lines.append(
            "- Kein Reject für diesen Song **mit dieser Folge**."
        )
    elif result.songs:
        lines.append(
            "- Kein Abgleich auf Folgen-Ebene möglich (Folge unklar)."
        )
    else:
        lines.append("- Kein Abgleich (Song unbekannt).")

    if other_rej:
        lines.append("")
        lines.append("Rejects dieses Songs bei anderen Folgen:")
        for h in other_rej[:6]:
            reason = (h.get("reason") or "").strip()
            short = reason if len(reason) <= 200 else reason[:197] + "…"
            lines.append(f"- Folge {h.get('episodeId')}: {short}")
    lines.append("")

    # Kurzfazit
    if same_rej:
        fazit = (
            "**Kurz:** Für diese Paarung gibt es schon einen Reject – "
            "vermutlich kein neuer Playlist-Eintrag."
        )
    elif same_pl:
        fazit = (
            "**Kurz:** Song/Folge steht schon in der Playlist – "
            "Issue eher Duplikat / Korrektur?"
        )
    elif not result.songs:
        fazit = (
            "**Kurz:** Song fehlt im Katalog – vor dem Matchen erst "
            "`songs.json` ergänzen."
        )
    else:
        fazit = (
            "**Kurz:** Kein bestehender Match/Reject für diese Paarung – "
            "Kandidat für manuelle Prüfung."
        )
    lines.extend([fazit, ""])
    return "\n".join(lines)


def build_from_args(args: argparse.Namespace) -> tuple[str, str, str]:
    band = args.band or ""
    title = args.title or ""
    folge = args.folge or ""

    body = ""
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8-sig")
    elif not sys.stdin.isatty() and not (band and title):
        body = sys.stdin.read()
    elif args.body:
        body = args.body

    if body:
        fields = parse_issue_form(body)
        band = band or form_get(fields, "Band")
        title = title or form_get(fields, "Songtitel", "Song", "Titel")
        folge = folge or form_get(fields, "GAG-Folge", "Folge", "Episode")

    return band, title, folge


def main(argv: list[str] | None = None) -> int:
    # Windows-Konsolen oft cp1252 – UTF-8 erzwingen, soweit möglich
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Triage für Playlist-Vorschlag-Issues"
    )
    parser.add_argument("--body", help="Issue-Body als String")
    parser.add_argument("--body-file", help="Issue-Body aus Datei")
    parser.add_argument("--band", help="Band (überschreibt Formular)")
    parser.add_argument("--title", help="Songtitel (überschreibt Formular)")
    parser.add_argument("--folge", help="GAG-Folge (überschreibt Formular)")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA,
        help="Pfad zu data/ (Default: Repo data/)",
    )
    parser.add_argument(
        "--comment-file",
        type=Path,
        help="Markdown-Kommentar hierher schreiben",
    )
    parser.add_argument(
        "--labels-file",
        type=Path,
        help="Empfohlene Labels (eine pro Zeile)",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Maschinenlesbares Ergebnis als JSON",
    )
    args = parser.parse_args(argv)

    band, title, folge = build_from_args(args)
    result = triage(band, title, folge, data_dir=args.data_dir)
    comment = format_comment(result)

    if args.comment_file:
        args.comment_file.write_text(comment, encoding="utf-8")
    else:
        print(comment)

    if args.labels_file:
        args.labels_file.write_text(
            "\n".join(result.labels) + ("\n" if result.labels else ""),
            encoding="utf-8",
        )

    if args.json_out:
        payload = {
            "band": result.band,
            "title": result.title,
            "folge_raw": result.folge_raw,
            "episode_id": result.episode_id,
            "episode_title": result.episode_title,
            "songs": [h.__dict__ for h in result.songs],
            "playlist_hit_count": len(result.playlist_hits),
            "reject_hit_count": len(result.reject_hits),
            "labels": result.labels,
            "notes": result.notes,
        }
        args.json_out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
