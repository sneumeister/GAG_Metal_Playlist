# -*- coding: utf-8 -*-
"""
Exportiert data/GAG_Metal_Playlist.json nach Markdown und HTML.

JSON-Quelle: Ordner `data/` (neben diesem Skript).
Ausgabe: Projektverzeichnis (eine Ebene höher):
  - GAG_Metal_playlist.md
  - GAG_Metal_playlist.html

Aufruf (aus dem Repo-Root oder aus data/):
  python data/export_playlist.py
  python export_playlist.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Paket `gag_export` liegt neben diesem Skript
_DATA_DIR = Path(__file__).resolve().parent
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))

from gag_export.common import HTML_NAME, JSON_NAME, MD_NAME, data_dir, output_dir  # noqa: E402
from gag_export.html import write_html  # noqa: E402
from gag_export.markdown import write_markdown  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GAG Metal Playlist → Markdown/HTML")
    parser.add_argument(
        "--md-only",
        action="store_true",
        help="Nur Markdown erzeugen",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Nur HTML erzeugen",
    )
    args = parser.parse_args(argv)

    json_path = data_dir() / JSON_NAME
    if not json_path.exists():
        print(f"Fehler: {json_path} nicht gefunden.", file=sys.stderr)
        return 1

    do_md = not args.html_only
    do_html = not args.md_only
    if args.md_only and args.html_only:
        do_md = do_html = True

    out = output_dir()
    if do_md:
        md_path = write_markdown(out / MD_NAME)
        print(f"geschrieben: {md_path}")
    if do_html:
        html_path = write_html(out / HTML_NAME)
        print(f"geschrieben: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
