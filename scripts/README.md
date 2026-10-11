# scripts/

Hilfsskripte für Folgen-Sync, Kandidaten-Queue und Issue-Triage.  
Stufen und Freigabe bleiben redaktionell (Rules `suchrunde`, `playlist-workflow`).  
Export der Listen: `python data/export_playlist.py`.

| Skript | Rolle |
| --- | --- |
| `sync_episodes.py` | Episoden-Snapshot aktualisieren: `fetchedAt` vs. Upstream-Commit, ID-Mengen-Diff, lokale Extra-Folgen behalten |
| `collect_candidates.py` | Offene Paare nach `_tmp_round.json` schreiben (ohne Stufe); neue Folgen gegen `songs.json` oder einzelnes Paar |
| `issue_triage.py` | Issue-Formular parsen; Duplikat-Hinweis gegen Katalog/Playlist/Rejects – keine Stufenentscheidung |
| `expand_catalog.py` | Alter Saat-Importer; schreibt nur mit `--apply-seed` – **kein** Suchlauf |

## Typischer Ablauf

```bash
python scripts/sync_episodes.py
python scripts/collect_candidates.py --episodes 577,578
# Issue-Paar:
python scripts/collect_candidates.py --band Sabaton --title Father --folge 157 --source issue
```

`scripts/_tmp_*` (inkl. `_tmp_round.json`) nicht committen; nach Freigabe leere Queue löschen.
