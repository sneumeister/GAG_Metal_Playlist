# Quellenkatalog

Quellen für Band-/Song-Recherche und Entity-Matching gegen GAG-Folgen.  
Stufen: **primär** (Song ↔ Thema belegbar), **sekundär** (Hilfreich, nicht alleiniger Beleg), **Seed** (Kandidaten finden).

## Primär

| Quelle | URL | Nutzen |
|--------|-----|--------|
| Sabaton Official / Historical Calendar | https://www.sabaton.net/ · https://www.sabaton.net/historical-calendar/ | Song ↔ historisches Ereignis |
| Sabaton History (YouTube) | https://www.youtube.com/@SabatonHistory | ausführliche Song-Hintergründe |
| Encyclopaedia Metallum | https://www.metal-archives.com/ | Band-Themes, Diskografie |
| Band-Sites, Liner Notes, Wikipedia-Songartikel | je Song | Subject / „based on“ |
| GAG-Folgendaten | https://github.com/ideadapt/geschichten-aus-der-geschichte-data (`data/episodes.jsonl`) | Folge-Titel, Beschreibung, Orte, Zeitbezüge |

## Sekundär

| Quelle | URL | Nutzen |
|--------|-----|--------|
| Genius / LyricFind | https://genius.com/ | Entity-Extraktion aus Lyrics – Gegenprüfung nötig |
| AZLyrics | https://www.azlyrics.com/ | Lyrics-Transcripts (nutzerseitig); Anti-Bot/Captcha, keine Annotationen – nur sekundär, nie alleiniger Match-Beleg |
| Sabaton-Fan-Index | https://elicarter.net/wiki/SabatonIndex | schnelle Song→Event-Übersicht |

## Seed (Community – nie alleiniger Match-Beleg)

| Quelle | Nutzen |
|--------|--------|
| Reddit r/sabaton, r/PowerMetal | Band-/Song-Ideen „historical / military lyrics“ |
| Fan-Listen „songs about historical events“ | weitere Kandidaten |
| GAG-Kommentare auf geschichte.fm | Hörervorschläge (Metal-Playlist) |

## Seed-Bands (Arbeitsreihenfolge)

1. **Sabaton** – Schlachten, Waffen, Personen (höchste Trefferwahrscheinlichkeit)
2. **Iron Maiden**, **Powerwolf** (Historien-Subset)
3. **Turisas**, **Running Wild**, **Grave Digger**, **Venom** (historische Einzeltracks)
4. Weitere: Civil War, Crystallion, Judicator, Serenity, Ex Deo, Warkings, Iced Earth, Rebellion, …

Siehe Plan: `plans/gag_song_matching.md`.
