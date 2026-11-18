# data/

Arbeitsdaten und Export für die GAG-Metal-Playlist. Matching-Regeln liegen unter [`.cursor/rules/`](../.cursor/rules), der Quellenkatalog unter [`docs/sources.md`](../docs/sources.md).

**JSON-Feldstrukturen:** [JSON_FORMAT.md](JSON_FORMAT.md)

| Datei / Ordner | Rolle |
| --- | --- |
| `GAG_Metal_Playlist.json` | **Metal-Treffer** – Objekt mit `updatedAt` und `entries` (Folge ↔ Song ↔ Begründung ↔ Links ↔ Tier A/B/C, `genre: "OK"`) |
| `GAG_Not_Metal_Playlist.json` | **Not-Metal-Treffer** – gleiches Schema, `genre: "NG"` (thematisch passend, kein Rock/Metal) |
| `songs.json` | Song-Katalog: Band, Titel, Entities, Era, Spotify/YouTube/Bandcamp, Quellen (ohne Wertung) |
| `rejected.json` | Geprüfte **inhaltliche** Absagen – Objekt mit `updatedAt` und `entries` (`episodeId` + `songId` + `reason` + …) |
| `episodes.jsonl` | Snapshot der GAG-Folgen (Titel, Beschreibung, Orte, Zeit) aus repo [`ideadapt/geschichten-aus-der-geschichte-data`](https://github.com/ideadapt/geschichten-aus-der-geschichte-data) |
| `episodes.meta.json` | Meta zum Snapshot (`sourceUrl`, `fetchedAt`) |
| `JSON_FORMAT.md` | Feldstrukturen der JSON-/JSONL-Dateien |
| `export_playlist.py` | Einstieg: Metal- + Not-Metal- + Reject-JSON → Markdown/HTML im Repo-Root |
| `gag_export/` | Export-Module (`common`, `markdown`, `html`) |

**Aufruf Export** (Repo-Root):

```bash
python data/export_playlist.py
```

Lesbare Ausgaben: `GAG_Metal_playlist.md` / `.html`, `GAG_Not_Metal_playlist.md` / `.html`, `GAG_Metal_rejected.md` / `.html` (mit gegenseitigen Links).
