#!/usr/bin/env python3
"""Preview the reply the Bible cog sends for a verse lookup.

Exercises the REAL lookup pipeline -- bundled verse data plus the live
Supernatural Bible Changes API -- and prints the rendered Discord embed.
Use it to iterate on the display format in bible/lookup_command.py:

    python scripts/preview_lookup.py "Genesis 1:1"
    python scripts/preview_lookup.py "John 3:16" --no-notes
    python scripts/preview_lookup.py "Genesis 1:1" --memories path/to/memories.json

By default a sample note is injected for the verse so the note block
renders alongside the verse and the change. Pass --no-notes to omit it,
or --memories to load real notes from a file.
"""
import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

# Make the repo root importable so `bible` resolves regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redbot.core import data_manager

# Point data_manager at a temp dir so the real load_memories() works.
_tmp = tempfile.mkdtemp()
data_manager.basic_config = {
    "DATA_PATH": _tmp,
    "COG_PATH_APPEND": "cogs",
    "CORE_PATH_APPEND": "core",
}

import bible.lookup_command as lookup_module
from bible.memories_store import load_memories as real_load_memories
from bible.search_utils import detect_translation, get_book_info, has_translation

# Real bundled data (bible/data/).
real_data = os.path.join(os.path.dirname(os.path.abspath(lookup_module.__file__)), "data")
lookup_module.bundled_data_path = lambda _cog: real_data


def _sample_note(verse_ref: str) -> dict:
    """Build a note that matches the requested verse so the note block renders."""
    translation = "akjv"
    ref = verse_ref
    if has_translation(ref):
        detected = detect_translation(ref)
        if detected:
            translation = detected
        ref = ref.rsplit(" ", 1)[0]

    book, _, cv = ref.rpartition(" ")
    book_info = get_book_info(book, translation)
    book_key = book_info["book"] if book_info else book.lower()

    if ":" in cv:
        chapter_s, verse_s = cv.split(":", 1)
        chapter = int(chapter_s)
        verse = int(verse_s.split("-")[0])
    else:
        chapter = int(cv)
        verse = 1

    return {
        "number": 1,
        "book": book_key,
        "chapter": chapter,
        "verse": verse,
        "note": f"Sample note for {verse_ref} (display preview).",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a Bible lookup reply.")
    parser.add_argument("verse", nargs="?", default="Genesis 1:1", help='e.g. "Genesis 1:1"')
    parser.add_argument("--memories", help="load notes from this memories.json")
    parser.add_argument("--no-notes", action="store_true", help="render no note block")
    args = parser.parse_args()

    if args.no_notes:
        notes = []
    elif args.memories:
        notes = real_load_memories(Path(args.memories))
    else:
        notes = [_sample_note(args.verse)]
    lookup_module.load_memories = lambda: notes

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    lookup_module.menu = fake_menu

    cog = SimpleNamespace()
    sent = []
    ctx = SimpleNamespace(send=lambda *a, **k: sent.append(a))

    asyncio.run(lookup_module.lookup(cog, ctx, args.verse))

    if sent:
        print("=== error path (ctx.send) ===")
        for s in sent:
            print(s)
        return

    embeds = captures.get("embeds", [])
    if not embeds:
        print("No embeds rendered.")
        return

    for i, e in enumerate(embeds):
        print(f"=== Embed {i + 1} of {len(embeds)} ===")
        print(f"Title : {e.title}")
        print(f"Color : #{e.color.value:06x}")
        print("--- Description ---")
        print(e.description)
        print("--- End ---")


if __name__ == "__main__":
    main()