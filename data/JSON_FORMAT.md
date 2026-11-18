# JSON-Formate unter `data/`

Feldstrukturen der kanonischen Datendateien. Rollen der Dateien: [README.md](README.md). Begründungsregeln: [`.cursor/rules/match-begruendungen.mdc`](../.cursor/rules/match-begruendungen.mdc).

Gemeinsam:

- Encoding: UTF-8 (`ensure_ascii=False` beim Schreiben).
- Fehlende Streaming-Links: `null` (Export zeigt `—`).
- `updatedAt` (Playlists / Rejects): `YYYY-MM-DD HH:MM:SS ±ZZZZ` (lokale Zeit mit Offset).

---

## `songs.json`

JSON-**Array** von Song-Objekten. Katalog ohne Wertung und ohne Folgen-Zuordnung.

| Feld | Typ | Pflicht | Bedeutung |
| --- | --- | --- | --- |
| `id` | string | ja | Stabile ID, z. B. `band-slug-title-slug` |
| `band` | string | ja | Bandname |
| `title` | string | ja | Songtitel |
| `entities` | string[] | ja | Historische Stichworte (kann `[]` sein) |
| `era` | string \| null | ja | Zeit-/Epochenhinweis |
| `spotifyUrl` | string \| null | ja* | Spotify-Track-URL |
| `youtubeUrl` | string \| null | ja* | YouTube-URL |
| `bandcampUrl` | string \| null | ja* | Bandcamp-Track-/Album-URL |
| `sources` | object[] | ja | Recherchequellen (kann `[]` sein) |

\*Feld vorhanden; Wert darf `null` sein.

### `sources[]`

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `type` | string | z. B. `lyrics`, `band`, `interview`, `discogs` |
| `url` | string | Quellen-URL |
| `note` | string | Kurznotiz |

---

## `GAG_Metal_Playlist.json` / `GAG_Not_Metal_Playlist.json`

JSON-**Objekt** mit denselben Feldern. Unterschied nur `genre`:

| Datei | `genre` |
| --- | --- |
| `GAG_Metal_Playlist.json` | immer `"OK"` (Rock/Metal) |
| `GAG_Not_Metal_Playlist.json` | immer `"NG"` (thematischer Treffer, kein Rock/Metal) |

### Objektebene

| Feld | Typ | Pflicht | Bedeutung |
| --- | --- | --- | --- |
| `updatedAt` | string | ja | Letzte inhaltliche Änderung |
| `entries` | object[] | ja | Treffer-Paare |

### `entries[]`

| Feld | Typ | Pflicht | Bedeutung |
| --- | --- | --- | --- |
| `episodeId` | number | ja | GAG-Folgennummer |
| `episodeTitle` | string | ja | Folgentitel (denormalisiert) |
| `episodeUrl` | string | ja | z. B. `https://gadg.fm/{id}` |
| `songId` | string | ja | FK → `songs.json` → `id` |
| `band` | string | ja | Band (denormalisiert) |
| `songTitle` | string | ja | Songtitel (denormalisiert) |
| `matchTier` | `"A"` \| `"B"` \| `"C"` | ja | Matching-Stufe |
| `justification` | string | ja | Begründung (Schlussformel siehe Rules) |
| `genre` | `"OK"` \| `"NG"` | ja | Metal vs. Not-Metal; **nicht** in Export-Tabellen |
| `spotifyUrl` | string \| null | ja* | oft aus Katalog übernommen |
| `youtubeUrl` | string \| null | ja* | oft aus Katalog übernommen |
| `bandcampUrl` | string \| null | ja* | oft aus Katalog übernommen |
| `sharedEntities` | string[] | nein | gemeinsame Stichworte (vor allem Metal) |
| `matchedAt` | string | nein | Datum `YYYY-MM-DD` |
| `curatedBy` | string | nein | z. B. `manual` |

\*Feld üblich; Wert darf `null` sein.

---

## `rejected.json`

JSON-**Objekt**. Nur **inhaltliche** Absagen (Stufe X). Band/Titel/Links stehen nicht hier — Export reichert aus `songs.json` + `episodes.jsonl` an.

### Objektebene

| Feld | Typ | Pflicht | Bedeutung |
| --- | --- | --- | --- |
| `updatedAt` | string | ja | Letzte inhaltliche Änderung |
| `entries` | object[] | ja | Absage-Paare |

### `entries[]`

| Feld | Typ | Pflicht | Bedeutung |
| --- | --- | --- | --- |
| `episodeId` | number | ja | GAG-Folgennummer |
| `songId` | string | ja | FK → `songs.json` → `id` |
| `reason` | string | ja | Absage-Begründung (endet mit `(Tier X).`) |
| `rejectedAt` | string | ja | Datum `YYYY-MM-DD` |
| `rejectedBy` | string | ja | z. B. `manual` |

---

## `episodes.jsonl`

Eine JSON-Zeile pro Folge (Snapshot aus [ideadapt/geschichten-aus-der-geschichte-data](https://github.com/ideadapt/geschichten-aus-der-geschichte-data)). Typische Felder:

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `id` | number | Folgennummer |
| `checksum` | number | Upstream-Checksum |
| `title` | string | Folgentitel |
| `date` | string | ISO-Datum (UTC) |
| `durationInSeconds` | number | Dauer |
| `websiteUrl` | string | z. B. gadg.fm-Link |
| `audioUrl` | string | Audio-URL |
| `description` | string | Folgenbeschreibung |
| `episodeLinks` | number[] | verwandte Folgen-IDs |
| `temporalLinks` | object[] | Zeitbezüge |
| `locations` | object[] | Orte (`name`, `latitude`, `longitude`) |

Pflege über `scripts/sync_episodes.py` (lokale Extra-Folgen möglich).

---

## `episodes.meta.json`

Meta zum Folgen-Snapshot:

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `lineCount` | number | Anzahl Zeilen in `episodes.jsonl` |
| `fetchedAt` | string | Abrufzeitpunkt (ISO UTC) |
| `sourceUrl` | string | Upstream-URL der `episodes.jsonl` |
