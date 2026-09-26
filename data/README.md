# data/

Arbeitsdaten und Export für die GAG-Metal-Playlist. Matching-Regeln und Quellenkatalog liegen unter `plans/` bzw. `docs/sources.md`.

| Datei / Ordner | Rolle |
| --- | --- |
| `GAG_Metal_Playlist.json` | **Kanonische Trefferliste** – Objekt mit `updatedAt` und `entries` (Folge ↔ Song ↔ Begründung ↔ Links ↔ Tier) |
| `songs.json` | Song-Katalog: Band, Titel, Entities, Era, Spotify/YouTube, Quellen |
| `rejected.json` | Geprüfte Absagen (`episodeId` + `songId` + Begründung), damit Kandidaten nicht erneut vorgeschlagen werden |
| `episodes.jsonl` | Snapshot der GAG-Folgen (Titel, Beschreibung, Orte, Zeit) |
| `episodes.meta.json` | Meta zum Snapshot (`sourceUrl`, `fetchedAt`) |
| `export_playlist.py` | Einstieg: JSON → Markdown/HTML im Repo-Root |
| `gag_export/` | Export-Module (`common`, `markdown`, `html`) |

**Aufruf Export** (Repo-Root):

```bash
python data/export_playlist.py
```

Lesbare Ausgaben: `GAG_Metal_playlist.md`, `GAG_Metal_playlist.html`.
