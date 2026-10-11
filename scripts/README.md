# scripts/

Hilfsskripte für Folgen-Sync, Kandidaten-Queue und Issue-Triage.  
Stufen und Freigabe bleiben redaktionell (Rules `suchrunde`, `playlist-workflow`).  
Export der Listen: `python data/export_playlist.py`.

| Skript | Rolle |
| --- | --- |
| `sync_episodes.py` | Episoden-Snapshot aktualisieren: `fetchedAt` vs. Upstream-Commit, ID-Mengen-Diff, lokale Extra-Folgen behalten |
| `collect_candidates.py` | Offene Paare nach `_tmp_round.json` (ohne Stufe); `--episodes` nur für **neue** IDs aus Sync, sonst Paar-Modus |
| `issue_triage.py` | Issue-Formular parsen; Duplikat-Hinweis gegen Katalog/Playlist/Rejects – keine Stufenentscheidung |
| `expand_catalog.py` | Alter Saat-Importer; schreibt nur mit `--apply-seed` – **kein** Suchlauf |

## Typischer Ablauf

```bash
python scripts/sync_episodes.py
# nur wenn Sync newEpisodeIds meldet:
python scripts/collect_candidates.py --episodes 577,578
# Issue-/Seed-Paar (kein Massen-Scan alter Folgen):
python scripts/collect_candidates.py --band Sabaton --title Father --folge 157 --source issue
```

Ohne neue IDs: Collect mit `--episodes` nicht aufrufen (Rule `suchrunde`).  
`scripts/_tmp_*` (inkl. `_tmp_round.json`) nicht committen; nach Freigabe leere Queue löschen.
