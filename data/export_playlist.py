# -*- coding: utf-8 -*-
"""
Exportiert Playlist-, Not-Metal- und Reject-JSON nach Markdown und HTML.

JSON-Quelle: Ordner `data/` (neben diesem Skript).
Ausgabe: Projektverzeichnis (eine Ebene höher):
  - GAG_Metal_playlist.md / .html
  - GAG_Not_Metal_playlist.md / .html
  - GAG_Metal_rejected.md / .html

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

from gag_export.common import (  # noqa: E402
    HTML_NAME,
    JSON_NAME,
    MD_NAME,
    NOT_METAL_HTML_NAME,
    NOT_METAL_JSON_NAME,
    NOT_METAL_MD_NAME,
    REJECT_HTML_NAME,
    REJECT_MD_NAME,
    REJECTED_JSON_NAME,
    data_dir,
    output_dir,
)
from gag_export.html import (  # noqa: E402
    write_html,
    write_not_metal_html,
    write_rejected_html,
)
from gag_export.markdown import (  # noqa: E402
    write_markdown,
    write_not_metal_markdown,
    write_rejected_markdown,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="GAG Metal / Not-Metal Playlist + Rejects → Markdown/HTML"
    )
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
    parser.add_argument(
        "--playlist-only",
        action="store_true",
        help="Nur Metal-Playlist-Export",
    )
    parser.add_argument(
        "--not-metal-only",
        action="store_true",
        help="Nur Not-Metal-Export",
    )
    parser.add_argument(
        "--rejected-only",
        action="store_true",
        help="Nur Reject-Export",
    )
    args = parser.parse_args(argv)

    playlist_json = data_dir() / JSON_NAME
    not_metal_json = data_dir() / NOT_METAL_JSON_NAME
    rejected_json = data_dir() / REJECTED_JSON_NAME

    only_flags = sum(
        bool(x) for x in (args.playlist_only, args.not_metal_only, args.rejected_only)
    )
    if only_flags == 0:
        do_playlist = do_not_metal = do_rejected = True
    else:
        do_playlist = args.playlist_only
        do_not_metal = args.not_metal_only
        do_rejected = args.rejected_only

    if do_playlist and not playlist_json.exists():
        print(f"Fehler: {playlist_json} nicht gefunden.", file=sys.stderr)
        return 1
    if do_not_metal and not not_metal_json.exists():
        print(f"Fehler: {not_metal_json} nicht gefunden.", file=sys.stderr)
        return 1
    if do_rejected and not rejected_json.exists():
        print(f"Fehler: {rejected_json} nicht gefunden.", file=sys.stderr)
        return 1

    do_md = not args.html_only
    do_html = not args.md_only
    if args.md_only and args.html_only:
        do_md = do_html = True

    out = output_dir()
    if do_playlist:
        if do_md:
            print(f"geschrieben: {write_markdown(out / MD_NAME)}")
        if do_html:
            print(f"geschrieben: {write_html(out / HTML_NAME)}")
    if do_not_metal:
        if do_md:
            print(f"geschrieben: {write_not_metal_markdown(out / NOT_METAL_MD_NAME)}")
        if do_html:
            print(f"geschrieben: {write_not_metal_html(out / NOT_METAL_HTML_NAME)}")
    if do_rejected:
        if do_md:
            print(f"geschrieben: {write_rejected_markdown(out / REJECT_MD_NAME)}")
        if do_html:
            print(f"geschrieben: {write_rejected_html(out / REJECT_HTML_NAME)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
