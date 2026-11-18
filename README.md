# GAG Metal Playlist

Zuordnung von Folgen des Podcasts [Geschichten aus der Geschichte](https://www.geschichte.fm/) (GAG) zu historisch passenden Rock-/Metal-Songs.

Ziel ist eine Trefferliste: **Folge ↔ Song ↔ Begründung ↔ Spotify/YouTube/Bandcamp-Link** — mit klaren Bezügen (Person, Schlacht, Ereignis, Ort) sowie schwächeren thematischen Nähen (Stufe C). Thematische Treffer ohne Rock/Metal landen in der Not-Metal-Liste; Absagen ohne brauchbaren Bezug als Stufe X.

## Aktuelle Listen

### Metal-Treffer (A/B/C)

- [Markdown](GAG_Metal_playlist.md)
- [HTML (GitHub)](GAG_Metal_playlist.html) · [Live (GitHub Pages, filter- und sortierbar)](https://sneumeister.github.io/GAG_Metal_Playlist/)

### Not-Metal-Treffer (A/B/C, kein Rock/Metal) ![Neu](https://img.shields.io/badge/Neu-e85d4c?style=flat-square)

- [Markdown](GAG_Not_Metal_playlist.md)
- [HTML (GitHub)](GAG_Not_Metal_playlist.html) · [Live (GitHub Pages, filter- und sortierbar)](https://sneumeister.github.io/GAG_Metal_Playlist/GAG_Not_Metal_playlist.html)

### Absagen (Stufe X)

- [Markdown](GAG_Metal_rejected.md)
- [HTML (GitHub)](GAG_Metal_rejected.html) · [Live (GitHub Pages, filter- und sortierbar)](https://sneumeister.github.io/GAG_Metal_Playlist/GAG_Metal_rejected.html)

Die Live-Ansicht läuft über GitHub Pages und rendert die HTML-Dateien im Browser.

## Matching-Stufen

- **A** – Song und Folge behandeln denselben Kerngegenstand (Person/Ereignis/Ort im Fokus).
- **B** – gemeinsamer historischer Rahmen mit klarer Überschneidung, aber klar anderem Fokus.
- **C** – erkennbare thematische/assoziative Nähe ohne gemeinsamen Erzählgegenstand; auch reine Inspiration/Metapher mit historischem Stichwort.
- **X** – inhaltlicher/thematischer Reject: kein brauchbarer Bezug (falsche Person/Phase/Ereignis, reiner Namens-/Zahlenanklang, …) → `data/rejected.json`.

Rock/Metal-Treffer A/B/C → Metal-Playlist (`genre: OK`). Thematisch passende Stücke ohne Rock/Metal → Not-Metal-Playlist (`genre: NG`, ebenfalls A/B/C).

## Mitmachen

Songvorschläge, Korrekturen und anderes Feedback:

- mit GitHub-Account: [Neues Issue öffnen](https://github.com/sneumeister/GAG_Metal_Playlist/issues/new/choose)
- ohne GitHub-Account: [Webformular](https://gag-playlist.sneumeister.de/)

## Hinweis

Dies ist ein **unabhängiges Fan-Projekt** und steht in keiner Verbindung zur GeschichteFM GmbH oder zum Podcast [Geschichten aus der Geschichte](https://www.geschichte.fm/). Es ist weder offiziell noch freigegeben.

Podcast-Titel, Folgeninhalte sowie Band- und Songnamen bleiben bei den jeweiligen Rechteinhabern. Hier entstehen nur Zuordnungen und Begründungen; es werden **keine** Audio-/Videodateien bereitgestellt, sondern Links zu Spotify, YouTube und – soweit auffindbar – Bandcamp.

Die Einstufung (Stufe A/B/C/X) und die Begründungen sind **redaktionelle Einschätzungen**. Für Richtigkeit, Vollständigkeit und erreichbare externe Links wird keine Haftung übernommen.

### Quellen

- Folgendaten: [ideadapt/geschichten-aus-der-geschichte-data](https://github.com/ideadapt/geschichten-aus-der-geschichte-data) (`episodes.jsonl`); Folgen-Links führen zu geschichte.fm / gadg.fm
- Song-Recherche und Entity-Matching: siehe [docs/sources.md](docs/sources.md)
- Streaming/Kauf: Drittanbieter-Links (Spotify, YouTube, Bandcamp); Verfügbarkeit und Region können abweichen; fehlende Spotify-/YouTube-/Bandcamp-Einträge sind als leer/`—` gekennzeichnet
