# -*- coding: utf-8 -*-
"""Expand song catalog and find new GAG matches."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(r"d:\Projekte\GAG_Metal_Playlist")
TODAY = "2026-09-26"
SRC_INDEX = {
    "type": "sabaton-index",
    "url": "https://elicarter.net/wiki/SabatonIndex",
}
SRC_OFFICIAL = {
    "type": "sabaton-official",
    "url": "https://www.sabaton.net/historical-calendar/",
}


def slug(s: str) -> str:
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def song_id(band: str, title: str) -> str:
    return f"{slug(band)}-{slug(title)}"


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mk_song(
    band: str,
    title: str,
    entities: list[str],
    era: str,
    *,
    spotify: str | None = None,
    youtube: str | None = None,
    sources: list[dict] | None = None,
    note: str | None = None,
) -> dict:
    src = sources or [{**SRC_INDEX, "note": note or title}]
    return {
        "id": song_id(band, title),
        "band": band,
        "title": title,
        "entities": entities,
        "era": era,
        "spotifyUrl": spotify,
        "youtubeUrl": youtube,
        "sources": src,
    }


# --- Sabaton historical catalog (primary studio/historical songs) ---
SABATON: list[dict] = [
    mk_song("Sabaton", "Primo Victoria", ["D-Day", "Normandie", "Operation Overlord"], "1944", note="D-Day / Normandy"),
    mk_song("Sabaton", "Reign of Terror", ["Operation Desert Storm", "Irak"], "1991"),
    mk_song("Sabaton", "Panzer Battalion", ["Irakkrieg", "2003"], "2003"),
    mk_song("Sabaton", "Wolfpack", ["U-Boot-Krieg", "Kriegsmarine", "Wolfsrudel Hecht"], "1942"),
    mk_song("Sabaton", "Counterstrike", ["Sechstagekrieg"], "1967"),
    mk_song(
        "Sabaton",
        "Stalingrad",
        ["Schlacht um Stalingrad", "Stalingrad", "6. Armee", "Friedrich Paulus"],
        "1942–1943",
    ),
    mk_song("Sabaton", "Into the Fire", ["Vietnamkrieg"], "1955–1975"),
    mk_song("Sabaton", "Attero Dominatus", ["Schlacht um Berlin", "Berlin 1945"], "1945"),
    mk_song("Sabaton", "Nuclear Attack", ["Hiroshima", "Nagasaki", "Atombombe"], "1945"),
    mk_song("Sabaton", "Rise of Evil", ["Hitler", "Aufstieg der NSDAP"], "1933–1939"),
    mk_song("Sabaton", "We Burn", ["Srebrenica", "1995"], "1995"),
    mk_song("Sabaton", "Angels Calling", ["Stellungskrieg", "Erster Weltkrieg"], "1914–1918"),
    mk_song("Sabaton", "Back in Control", ["Falklandkrieg"], "1982"),
    mk_song("Sabaton", "Light in the Black", ["UN-Friedenstruppen", "Peacekeeping"], "1945–"),
    mk_song("Sabaton", "Ghost Division", ["7. Panzer-Division", "Rommel", "Geisterdivision"], "1940"),
    mk_song("Sabaton", "40:1", ["Schlacht von Wizna", "Polen 1939"], "1939"),
    mk_song("Sabaton", "Cliffs of Gallipoli", ["Gallipoli", "Dardanellen", "Erster Weltkrieg"], "1915–1916"),
    mk_song("Sabaton", "Talvisota", ["Winterkrieg", "Finnland", "Sowjetunion"], "1939–1940"),
    mk_song("Sabaton", "Panzerkampf", ["Schlacht bei Kursk"], "1943"),
    mk_song("Sabaton", "Union (Slopes of St. Benedict)", ["Monte Cassino"], "1944"),
    mk_song("Sabaton", "The Price of a Mile", ["Passchendaele", "Erster Weltkrieg"], "1917"),
    mk_song("Sabaton", "Firestorm", ["strategischer Bombenkrieg"], "1939–1945"),
    mk_song("Sabaton", "Swedish Pagans", ["Wikinger", "Rus", "Skandinavien"], "Wikingerzeit"),
    mk_song("Sabaton", "Coat of Arms", ["Griechisch-Italienischer Krieg"], "1940–1941"),
    mk_song("Sabaton", "Midway", ["Schlacht um Midway"], "1942"),
    mk_song("Sabaton", "Uprising", ["Warschauer Aufstand"], "1944"),
    mk_song("Sabaton", "Screaming Eagles", ["101st Airborne", "Bastogne"], "1944"),
    mk_song("Sabaton", "The Final Solution", ["Holocaust", "Shoah"], "1941–1945"),
    mk_song("Sabaton", "Aces in Exile", ["Schlacht um England", "RAF", "Exilpiloten"], "1940"),
    mk_song(
        "Sabaton",
        "Saboteurs",
        ["Schwerwasser-Sabotage", "Vemork", "Norwegen", "Telemark", "Zweiter Weltkrieg"],
        "1942–1943",
        spotify="https://open.spotify.com/track/3bJdPt4et4xZnWKMFR6orf",
    ),
    mk_song("Sabaton", "Wehrmacht", ["Wehrmacht"], "1935–1945"),
    mk_song("Sabaton", "White Death", ["Simo Häyhä", "Weißer Tod", "Winterkrieg"], "1939–1940"),
    mk_song(
        "Sabaton",
        "The Lion from the North",
        ["Gustav II. Adolf", "Dreißigjähriger Krieg"],
        "1611–1632",
    ),
    mk_song("Sabaton", "Gott mit uns", ["Breitenfeld", "Gustav II. Adolf"], "1631"),
    mk_song(
        "Sabaton",
        "A Lifetime of War",
        ["Dreißigjähriger Krieg"],
        "1618–1648",
    ),
    mk_song("Sabaton", "1648", ["Westfälischer Friede", "Dreißigjähriger Krieg"], "1648"),
    mk_song("Sabaton", "The Carolean's Prayer", ["Karoliner", "schwedische Armee"], "1682–"),
    mk_song(
        "Sabaton",
        "Carolus Rex",
        ["Karl XII.", "Carolus Rex", "Schweden", "Großer Nordischer Krieg"],
        "1697–1718",
        spotify="https://open.spotify.com/track/65WiP6G7rRBTLNxDzwam3M",
    ),
    mk_song("Sabaton", "Killing Ground", ["Schlacht bei Fraustadt"], "1706"),
    mk_song(
        "Sabaton",
        "Poltava",
        ["Schlacht bei Poltawa", "Karl XII.", "Peter I.", "Großer Nordischer Krieg"],
        "1709",
        spotify="https://open.spotify.com/track/4Bkov6Yhi63EFOZUNMKbtf",
    ),
    mk_song("Sabaton", "Long Live the King", ["Karl XII.", "Tod Karls XII."], "1718"),
    mk_song("Sabaton", "Ruina Imperii", ["Ende des Schwedischen Reichs", "Karl XII."], "1718–1721"),
    mk_song("Sabaton", "Night Witches", ["Nachthexen", "588. Nachtbomberregiment"], "1942–1945"),
    mk_song("Sabaton", "No Bullets Fly", ["Franz Stigler", "Charlie Brown"], "1943"),
    mk_song("Sabaton", "Smoking Snakes", ["Brasilianisches Expeditionskorps", "Po-Ebene"], "1944–1945"),
    mk_song("Sabaton", "Inmate 4859", ["Witold Pilecki", "Auschwitz"], "1940–1943"),
    mk_song("Sabaton", "To Hell and Back", ["Audie Murphy"], "1945"),
    mk_song("Sabaton", "The Ballad of Bull", ["Leslie Bull Allen"], "1943"),
    mk_song("Sabaton", "Resist and Bite", ["Chasseurs Ardennais"], "1940"),
    mk_song("Sabaton", "Soldier of 3 Armies", ["Lauri Törni", "Larry Thorne"], "1939–1965"),
    mk_song("Sabaton", "Far from the Fame", ["Karel Janoušek", "Schlacht um England"], "1940"),
    mk_song(
        "Sabaton",
        "Hearts of Iron",
        ["Schlacht um Berlin", "Walther Wenck", "12. Armee", "Berlin 1945"],
        "1945",
        sources=[
            {**SRC_OFFICIAL, "note": "Wenck / Battle of Berlin — nicht 6. Armee/Stalingrad"},
            {**SRC_INDEX, "note": "Hearts of Iron"},
        ],
    ),
    mk_song(
        "Sabaton",
        "Sparta",
        ["Thermopylen", "Leonidas", "Sparta", "Perserkriege", "300 Spartaner"],
        "480 v. Chr.",
        spotify="https://open.spotify.com/track/5GiBUJsWN6jrCPEbHRuG9T",
    ),
    mk_song("Sabaton", "Last Dying Breath", ["Belgrad 1915", "Serbien"], "1915"),
    mk_song("Sabaton", "Blood of Bannockburn", ["Bannockburn", "Robert the Bruce"], "1314"),
    mk_song("Sabaton", "The Lost Battalion", ["Lost Battalion", "Argonnen"], "1918"),
    mk_song("Sabaton", "Rorke's Drift", ["Rorke's Drift", "Anglo-Zulu-Krieg"], "1879"),
    mk_song(
        "Sabaton",
        "The Last Stand",
        ["Schweizergarde", "Sacco di Roma", "Plünderung Roms 1527"],
        "1527",
    ),
    mk_song("Sabaton", "Hill 3234", ["Hügel 3234", "Sowjetisch-Afghanischer Krieg"], "1988"),
    mk_song("Sabaton", "Shiroyama", ["Shiroyama", "Satsuma-Rebellion", "Saigō Takamori"], "1877"),
    mk_song(
        "Sabaton",
        "Winged Hussars",
        ["Zweite Wiener Türkenbelagerung", "Entsatz von Wien", "Flügelhusaren", "1683"],
        "1683",
    ),
    mk_song(
        "Sabaton",
        "The Last Battle",
        ["Schloss Itter", "Castle Itter", "Tirol", "Zweiter Weltkrieg"],
        "1945",
        spotify="https://open.spotify.com/track/0NjHYeO88VsXEd9VEu538C",
    ),
    mk_song("Sabaton", "Bismarck", ["Schlachtschiff Bismarck"], "1941"),
    mk_song("Sabaton", "The Future of Warfare", ["Panzer", "Flers-Courcelette"], "1916"),
    mk_song("Sabaton", "Seven Pillars of Wisdom", ["T. E. Lawrence", "Lawrence von Arabien"], "1916–1918"),
    mk_song("Sabaton", "82nd All the Way", ["Alvin York", "82nd Division"], "1918"),
    mk_song(
        "Sabaton",
        "The Attack of the Dead Men",
        ["Osowiec", "Festung Osowiec", "Gasangriff"],
        "1915",
    ),
    mk_song("Sabaton", "Devil Dogs", ["Belleau Wood", "US Marines"], "1918"),
    mk_song("Sabaton", "The Red Baron", ["Manfred von Richthofen", "Roter Baron"], "1916–1918"),
    mk_song("Sabaton", "Great War", ["Erster Weltkrieg", "Passchendaele"], "1914–1918"),
    mk_song("Sabaton", "A Ghost in the Trenches", ["Francis Pegahmagabow"], "1914–1918"),
    mk_song("Sabaton", "Fields of Verdun", ["Schlacht um Verdun"], "1916"),
    mk_song("Sabaton", "The End of the War to End All Wars", ["Waffenstillstand von Compiègne"], "1918"),
    mk_song("Sabaton", "Christmas Truce", ["Weihnachtsfrieden 1914"], "1914"),
    mk_song("Sabaton", "Soldier of Heaven", ["Alpenfront", "Erster Weltkrieg"], "1915–1918"),
    mk_song("Sabaton", "The Unkillable Soldier", ["Adrian Carton de Wiart"], "1914–1918"),
    mk_song("Sabaton", "Sarajevo", ["Attentat von Sarajevo", "Franz Ferdinand"], "1914"),
    mk_song("Sabaton", "Stormtroopers", ["Stoßtruppen", "Erster Weltkrieg"], "1915–1918"),
    mk_song("Sabaton", "Dreadnought", ["Dreadnought", "Skagerrakschlacht", "Jütland"], "1916"),
    mk_song("Sabaton", "Hellfighters", ["Harlem Hellfighters", "369th Infantry"], "1918"),
    mk_song("Sabaton", "Race to the Sea", ["Albert I. von Belgien", "Yser"], "1914"),
    mk_song("Sabaton", "Lady of the Dark", ["Milunka Savić"], "1912–1918"),
    mk_song("Sabaton", "Valley of Death", ["Schlacht von Doiran"], "1917"),
    mk_song("Sabaton", "Versailles", ["Versailler Vertrag"], "1919"),
    mk_song(
        "Sabaton",
        "Father",
        ["Fritz Haber", "Haber-Bosch-Verfahren", "Giftgas", "chemischer Krieg", "Erster Weltkrieg"],
        "1909/1915",
        spotify="https://open.spotify.com/track/6pPCkAzVYapjObH73BWu9t",
        sources=[
            {**SRC_OFFICIAL, "note": "Fritz Haber / Haber-Bosch"},
            {**SRC_INDEX, "note": "Father"},
        ],
    ),
    mk_song("Sabaton", "1916", ["Kindersoldaten", "Erster Weltkrieg"], "1916"),
    mk_song("Sabaton", "The First Soldier", ["Albert Severin Roche"], "1914–1918"),
    mk_song(
        "Sabaton",
        "Templars",
        ["Templerorden", "Jacques de Molay", "Philipp IV.", "Jerusalem", "Kreuzzüge"],
        "1119–1307",
        spotify="https://open.spotify.com/track/6VS9iSOD6IuZXoLZblFzjy",
        youtube="https://www.youtube.com/watch?v=B10ECkQXQtU",
        sources=[
            {
                "type": "sabaton-official",
                "url": "https://www.sabaton.net/discography/templars/",
                "note": "Knights Templar rise and fall",
            }
        ],
    ),
    mk_song("Sabaton", "Hordes of Khan", ["Dschingis Khan", "Mongolenreich"], "13. Jh."),
    mk_song("Sabaton", "Crossing the Rubicon", ["Rubikon", "Julius Caesar"], "49 v. Chr."),
    mk_song("Sabaton", "Yamato", ["Schlachtschiff Yamato"], "1945"),
    mk_song("Sabaton", "Livgardet", ["Livgardet", "schwedische Leibgarde"], "1521–"),
]

# --- Iron Maiden (historisches Subset) ---
MAIDEN = [
    mk_song(
        "Iron Maiden",
        "Alexander the Great",
        ["Alexander der Große", "Makedonien", "Alexandria"],
        "356–323 v. Chr.",
        sources=[{"type": "wikipedia", "url": "https://en.wikipedia.org/wiki/Alexander_the_Great_(song)", "note": "biographical lyrics"}],
    ),
    mk_song(
        "Iron Maiden",
        "The Trooper",
        ["Charge of the Light Brigade", "Balaclava", "Krimkrieg"],
        "1854",
        sources=[{"type": "secondary", "url": "https://www.loudersound.com/features/the-11-best-iron-maiden-songs-based-on-history", "note": "Balaclava"}],
    ),
    mk_song(
        "Iron Maiden",
        "Aces High",
        ["Schlacht um England", "Battle of Britain", "RAF"],
        "1940",
        sources=[{"type": "secondary", "url": "https://www.loudersound.com/features/the-11-best-iron-maiden-songs-based-on-history", "note": "Battle of Britain"}],
    ),
    mk_song(
        "Iron Maiden",
        "Paschendale",
        ["Passchendaele", "Erster Weltkrieg", "Flandern"],
        "1917",
        sources=[{"type": "secondary", "url": "https://www.loudersound.com/features/the-11-best-iron-maiden-songs-based-on-history", "note": "Passchendaele"}],
    ),
    mk_song(
        "Iron Maiden",
        "Run to the Hills",
        ["Kolonisierung Nordamerikas", "First Nations"],
        "17.–19. Jh.",
        sources=[{"type": "secondary", "url": "https://www.loudersound.com/features/the-11-best-iron-maiden-songs-based-on-history", "note": "Native American conflict"}],
    ),
    mk_song(
        "Iron Maiden",
        "The Longest Day",
        ["D-Day", "Normandie", "Operation Overlord"],
        "1944",
        sources=[{"type": "seed", "url": "https://www.reddit.com/r/ironmaiden/comments/g2k2l0/historical_based_songs/", "note": "D-Day"}],
    ),
    mk_song(
        "Iron Maiden",
        "Montségur",
        ["Montségur", "Katharer", "Albigenserkreuzzug"],
        "1244",
        sources=[{"type": "seed", "url": "https://www.reddit.com/r/ironmaiden/comments/g2k2l0/historical_based_songs/", "note": "Montségur"}],
    ),
    mk_song(
        "Iron Maiden",
        "Empire of the Clouds",
        ["R101", "Luftschiffabsturz"],
        "1930",
        sources=[{"type": "seed", "url": "https://www.reddit.com/r/ironmaiden/comments/g2k2l0/historical_based_songs/", "note": "R101"}],
    ),
    mk_song(
        "Iron Maiden",
        "Genghis Khan",
        ["Dschingis Khan", "Mongolenreich"],
        "13. Jh.",
        sources=[{"type": "seed", "url": "https://www.reddit.com/r/ironmaiden/comments/g2k2l0/historical_based_songs/", "note": "Genghis Khan"}],
    ),
]

# --- Powerwolf (Historien-Subset) ---
POWERWOLF = [
    mk_song(
        "Powerwolf",
        "Beast of Gévaudan",
        ["Bestie des Gévaudan", "Gévaudan", "Frankreich 18. Jh."],
        "1764–1767",
        sources=[
            {
                "type": "band-official",
                "url": "https://www.powerwolf.net/news/news-archive?catid=10&id=39&view=article",
                "note": "Beast of Gévaudan",
            }
        ],
    ),
    mk_song(
        "Powerwolf",
        "1589",
        ["Peter Stumpp", "Werwolf von Bedburg", "1589"],
        "1589",
        sources=[
            {
                "type": "wikipedia",
                "url": "https://en.wikipedia.org/wiki/Peter_Stumpp",
                "note": "Werewolf of Bedburg / Powerwolf 1589",
            }
        ],
    ),
    mk_song(
        "Powerwolf",
        "Joan of Arc",
        ["Jeanne d'Arc", "Joan of Arc", "Orléans"],
        "1412–1431",
        sources=[
            {
                "type": "secondary",
                "url": "https://en.wikipedia.org/wiki/Powerwolf_discography",
                "note": "Joan of Arc (2024/25 album track)",
            }
        ],
    ),
]

# --- Turisas ---
TURISAS = [
    mk_song(
        "Turisas",
        "The March of the Varangian Guard",
        ["Warägergarde", "Byzanz", "Konstantinopel", "Miklagard"],
        "11. Jh.",
        sources=[
            {
                "type": "secondary",
                "url": "https://en.wikipedia.org/wiki/Stand_Up_and_Fight_(album)",
                "note": "Varangian Guard concept album",
            }
        ],
    ),
    mk_song(
        "Turisas",
        "Stand Up and Fight",
        ["Warägergarde", "Byzanz", "Konstantinopel"],
        "11. Jh.",
        sources=[
            {
                "type": "secondary",
                "url": "https://en.wikipedia.org/wiki/Stand_Up_and_Fight_(album)",
                "note": "title track / Varangian Guard",
            }
        ],
    ),
    mk_song(
        "Turisas",
        "Miklagard Overture",
        ["Miklagard", "Konstantinopel", "Waräger", "Byzanz"],
        "9.–11. Jh.",
        sources=[
            {
                "type": "secondary",
                "url": "https://www.medievalists.net/2019/10/heavy-metal-meets-byzantium/",
                "note": "Varangian Way ends in Constantinople",
            }
        ],
    ),
    mk_song(
        "Turisas",
        "To Holmgard and Beyond",
        ["Warägerweg", "Holmgard", "Nowgorod", "Rus"],
        "9.–11. Jh.",
        sources=[
            {
                "type": "secondary",
                "url": "https://bravewords.com/news/turisas-announce-details-of-new-studio-album-the-varangian-way/",
                "note": "Varangian Way concept",
            }
        ],
    ),
    mk_song(
        "Turisas",
        "In the Court of Jarisleif",
        ["Jaroslaw der Weise", "Kiew", "Waräger"],
        "11. Jh.",
        sources=[
            {
                "type": "secondary",
                "url": "https://bravewords.com/news/turisas-announce-details-of-new-studio-album-the-varangian-way/",
                "note": "Jarisleif = Yaroslav",
            }
        ],
    ),
]


def merge_songs(existing: list[dict], new_songs: list[dict]) -> list[dict]:
    by_id = {s["id"]: s for s in existing}
    for s in new_songs:
        if s["id"] in by_id:
            old = by_id[s["id"]]
            # preserve existing URLs if new ones are null
            if old.get("spotifyUrl") and not s.get("spotifyUrl"):
                s["spotifyUrl"] = old["spotifyUrl"]
            if old.get("youtubeUrl") and not s.get("youtubeUrl"):
                s["youtubeUrl"] = old["youtubeUrl"]
        by_id[s["id"]] = s
    # stable-ish order: band then title
    return sorted(by_id.values(), key=lambda x: (x["band"].lower(), x["title"].lower()))


def find_eps(eps: list[dict], pattern: str) -> list[dict]:
    rx = re.compile(pattern, re.I)
    out = []
    for e in eps:
        blob = f"{e.get('title', '')}\n{e.get('description', '')}"
        if rx.search(blob):
            out.append(e)
    return out


def main() -> None:
    songs_path = ROOT / "data" / "songs.json"
    matches_path = ROOT / "data" / "GAG_Metal_Playlist.json"
    rejected_path = ROOT / "data" / "rejected.json"

    existing_songs = load_json(songs_path, [])
    songs = merge_songs(existing_songs, SABATON + MAIDEN + POWERWOLF + TURISAS)
    save_json(songs_path, songs)
    by_id = {s["id"]: s for s in songs}

    eps = []
    for line in (ROOT / "data" / "episodes.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            eps.append(json.loads(line))
    ep_by_id = {e["id"]: e for e in eps}

    raw_matches = load_json(matches_path, {"updatedAt": TODAY, "entries": []})
    if isinstance(raw_matches, list):
        matches = raw_matches
    else:
        matches = list(raw_matches.get("entries") or [])
    rejected = load_json(rejected_path, [])
    decided = {(m["episodeId"], m["songId"]) for m in matches}
    decided |= {(r["episodeId"], r["songId"]) for r in rejected}

    def add_match(ep_id: int, song_id: str, tier: str, justification: str, shared: list[str]) -> bool:
        key = (ep_id, song_id)
        if key in decided:
            return False
        ep = ep_by_id[ep_id]
        song = by_id[song_id]
        matches.append(
            {
                "episodeId": ep["id"],
                "episodeTitle": ep["title"],
                "episodeUrl": ep["websiteUrl"],
                "songId": song["id"],
                "band": song["band"],
                "songTitle": song["title"],
                "matchTier": tier,
                "justification": justification,
                "sharedEntities": shared,
                "spotifyUrl": song.get("spotifyUrl"),
                "youtubeUrl": song.get("youtubeUrl"),
                "matchedAt": TODAY,
                "curatedBy": "manual",
            }
        )
        decided.add(key)
        return True

    def add_reject(ep_id: int, song_id: str, reason: str) -> bool:
        key = (ep_id, song_id)
        if key in decided:
            return False
        rejected.append(
            {
                "episodeId": ep_id,
                "songId": song_id,
                "reason": reason,
                "rejectedAt": TODAY,
                "rejectedBy": "manual",
            }
        )
        decided.add(key)
        return True

    new_m = 0
    new_r = 0

    # Powerwolf / Gévaudan
    for e in find_eps(eps, r"Bestie des G.?vaudan|Gévaudan|Gevaudan"):
        if add_match(
            e["id"],
            "powerwolf-beast-of-gevaudan",
            "A",
            "Beide behandeln die Bestie des Gévaudan (Frankreich, 1760er).",
            ["Bestie des Gévaudan", "Gévaudan"],
        ):
            new_m += 1

    # Jeanne d'Arc
    for e in find_eps(eps, r"Jeanne d.?Arc|Joan of Arc|Jungfrau von Orl"):
        if add_match(
            e["id"],
            "powerwolf-joan-of-arc",
            "A",
            "Beide beziehen sich auf Jeanne d'Arc.",
            ["Jeanne d'Arc"],
        ):
            new_m += 1

    # Werwolf / Bedburg / Stumpp / Wiedergänger-Folgen
    for e in find_eps(eps, r"Peter Stumpp|Werwolf von Bedburg|Bedburg"):
        if add_match(
            e["id"],
            "powerwolf-1589",
            "A",
            "Beide behandeln Peter Stumpp / den Werwolf von Bedburg (1589).",
            ["Peter Stumpp", "Werwolf von Bedburg", "1589"],
        ):
            new_m += 1

    # Alexander
    for e in find_eps(eps, r"Alexander der Gro(ss|ß)e|Alexander the Great"):
        if add_match(
            e["id"],
            "iron-maiden-alexander-the-great",
            "A",
            "Beide behandeln Alexander den Großen.",
            ["Alexander der Große"],
        ):
            new_m += 1

    # Charge of the Light Brigade — GAG290
    for e in find_eps(eps, r"Leichten Brigade|Balaclava|Charge of the Light"):
        if add_match(
            e["id"],
            "iron-maiden-the-trooper",
            "A",
            "Beide behandeln die Attacke der Leichten Brigade / Balaclava (Krimkrieg).",
            ["Charge of the Light Brigade", "Balaclava", "Krimkrieg"],
        ):
            new_m += 1

    # Montségur / Katharer
    for e in find_eps(eps, r"Monts.?gur"):
        if add_match(
            e["id"],
            "iron-maiden-montsegur",
            "A",
            "Beide behandeln Montségur / die Katharerfestung.",
            ["Montségur", "Katharer"],
        ):
            new_m += 1

    # R101
    for e in find_eps(eps, r"\bR101\b"):
        if add_match(
            e["id"],
            "iron-maiden-empire-of-the-clouds",
            "A",
            "Beide behandeln den Absturz des Luftschiffs R101.",
            ["R101"],
        ):
            new_m += 1

    # Turisas / Warägergarde
    for e in find_eps(eps, r"Warägergarde|Waragergarde"):
        if add_match(
            e["id"],
            "turisas-the-march-of-the-varangian-guard",
            "A",
            "Beide behandeln die Warägergarde am byzantinischen Hof.",
            ["Warägergarde", "Byzanz"],
        ):
            new_m += 1
        if add_match(
            e["id"],
            "turisas-stand-up-and-fight",
            "A",
            "Stand Up and Fight stammt vom Warägergarde-Konzeptalbum; die Folge behandelt dieselbe Leibgarde.",
            ["Warägergarde", "Byzanz"],
        ):
            new_m += 1

    # Ibn Fadlan — related to Varangian route / Rus (strong B with Holmgard song?)
    for e in find_eps(eps, r"Ibn Fadl"):
        if add_match(
            e["id"],
            "turisas-to-holmgard-and-beyond",
            "B",
            "Ibn Fadlan beschreibt die Rus/Waräger auf der Wolga-Route; Turisas’ Varangian-Way-Album thematisiert denselben Warägerweg nach Osten.",
            ["Waräger", "Rus", "Wolga-Route"],
        ):
            new_m += 1

    # Sabaton: Long Live the King / Ruina Imperii for Karl XII episode
    if add_match(
        471,
        "sabaton-long-live-the-king",
        "A",
        "Die Folge behandelt u. a. Tod und Rätsel um Karl XII.; der Song gilt dem Tod des Königs.",
        ["Karl XII."],
    ):
        new_m += 1
    if add_match(
        471,
        "sabaton-ruina-imperii",
        "B",
        "Die Folge thematisiert das Ende des schwedischen Großreichs nach Karl XII.; „Ruina Imperii“ ebenso.",
        ["Ende des Schwedischen Reichs", "Karl XII."],
    ):
        new_m += 1

    # Lion from the North / Gott mit uns — only if 30YW episode exists
    for e in find_eps(eps, r"Gustav II\.? Adolf|Gustav Adolf|Breitenfeld"):
        if add_match(
            e["id"],
            "sabaton-the-lion-from-the-north",
            "A",
            "Beide behandeln Gustav II. Adolf.",
            ["Gustav II. Adolf"],
        ):
            new_m += 1

    # Dschingis — Hordes of Khan / Maiden Genghis if episode
    for e in find_eps(eps, r"Dschingis|Genghis Khan|Tschingis"):
        if add_match(
            e["id"],
            "sabaton-hordes-of-khan",
            "A",
            "Beide behandeln Dschingis Khan / die Mongolen.",
            ["Dschingis Khan"],
        ):
            new_m += 1

    # Caesar Rubicon
    for e in find_eps(eps, r"Rubikon|Rubicon"):
        if add_match(
            e["id"],
            "sabaton-crossing-the-rubicon",
            "A",
            "Beide behandeln Caesars Überschreitung des Rubikon.",
            ["Rubikon", "Julius Caesar"],
        ):
            new_m += 1

    # Weak rejects worth documenting if we looked
    # Battle of Britain vs Aces High — only if GAG has dedicated episode
    # Paschendale / Verdun / Gallipoli — no GAG hits earlier

    # Jeanne false positives already handled by regex

    # Sort matches
    matches.sort(key=lambda m: (m["episodeId"], m["band"], m["songTitle"]))
    save_json(matches_path, {"updatedAt": TODAY, "entries": matches})
    save_json(rejected_path, rejected)

    print(f"songs={len(songs)} matches={len(matches)} (+{new_m}) rejected={len(rejected)} (+{new_r})")

    # Print candidate hits for manual review dump
    print("\n--- search hits ---")
    for label, pat in [
        ("Gevaudan", r"Bestie des G.?vaudan|Gévaudan"),
        ("Jeanne", r"Jeanne d.?Arc|Joan of Arc"),
        ("Bedburg", r"Stumpp|Bedburg|Werwolf von"),
        ("Alexander", r"Alexander der Gro(ss|ß)e"),
        ("LightBrigade", r"Leichten Brigade|Balaclava"),
        ("Montsegur", r"Monts.?gur"),
        ("R101", r"\bR101\b"),
        ("Warager", r"Warägergarde"),
        ("IbnFadlan", r"Ibn Fadl"),
        ("GustavAdolf", r"Gustav II\.? Adolf|Gustav Adolf|Breitenfeld"),
        ("Genghis", r"Dschingis|Genghis"),
        ("Rubicon", r"Rubikon|Rubicon"),
        ("Vampir", r"Vampir|Wiedergänger|Plogojowitz|Werwolf"),
    ]:
        hits = find_eps(eps, pat)
        if hits:
            print(f"{label}: " + "; ".join(f"{h['id']}:{h['title']}" for h in hits[:8]))


if __name__ == "__main__":
    main()
