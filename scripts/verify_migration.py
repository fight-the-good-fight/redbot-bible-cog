#!/usr/bin/env python3
"""
Verify the migrated data-live files against the cog code.

Checks that new-memories.json loads through the cog's memories_store, that
every note's book resolves and satisfies the lookup matching rule, that
numbering is sequential, and that the notes match the legacy settings
(reference set, text after the "Commentary: " prefix strip).

Run with the venv python so the cog imports resolve:
    .venv/bin/python scripts/verify_migration.py
    .venv/bin/python scripts/verify_migration.py --memories ... --settings ...
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bible.memories_store import load_memories
from bible.search_utils import get_book_info

# legacy dart-app book keys that map to the cog's normalized book names
# (kept in sync with scripts/migrate_memories.py)
BOOK_NAME_MAP = {"1Enoch": "Enoch"}
NOTE_KEYS = {"number", "book", "chapter", "verse", "note"}
LEGACY_PREFIX = "Commentary: "


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify migrated memories/settings files")
    parser.add_argument(
        "--memories",
        default="data-live/new-memories.json",
        help="migrated memories file (default: %(default)s)",
    )
    parser.add_argument(
        "--settings",
        default="data-live/settings.json",
        help="legacy cog settings.json (default: %(default)s)",
    )
    parser.add_argument(
        "--new-settings",
        default="data-live/new-settings.json",
        help="migrated settings file (default: %(default)s)",
    )
    args = parser.parse_args()

    failures = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            failures += 1

    memories = load_memories(Path(args.memories))
    check("memories loaded", len(memories) > 0, f"count={len(memories)}")

    check(
        "note shape",
        all(set(m) == NOTE_KEYS for m in memories),
        "expected keys: " + ", ".join(sorted(NOTE_KEYS)),
    )

    bad_books = sorted({m["book"] for m in memories if get_book_info(m["book"]) is None})
    check("all books resolve", not bad_books, f"unresolvable: {bad_books}")

    mismatch = [
        m["book"]
        for m in memories
        if get_book_info(m["book"]) is not None
        and m["book"].lower() != get_book_info(m["book"])["book"]
    ]
    check("lookup matching rule holds", not mismatch, f"mismatched: {sorted(set(mismatch))}")

    check(
        "numbers sequential",
        [m["number"] for m in memories] == list(range(1, len(memories) + 1)),
    )

    legacy = json.loads(Path(args.settings).read_text(encoding="utf-8"))
    legacy_notes = []
    for data in legacy.values():
        legacy_notes.extend(data.get("GLOBAL", {}).get("Notes", []))

    legacy_by_ref = {
        (BOOK_NAME_MAP.get(n["book"], n["book"]), n["chapter"], n["verse"]): n["note"]
        for n in legacy_notes
    }
    new_by_ref = {(m["book"], m["chapter"], m["verse"]): m["note"] for m in memories}

    check(
        "reference set matches legacy",
        set(legacy_by_ref) == set(new_by_ref),
        f"legacy={len(legacy_by_ref)} new={len(new_by_ref)}",
    )

    text_diffs = [
        k
        for k in new_by_ref
        if k in legacy_by_ref
        and legacy_by_ref[k].removeprefix(LEGACY_PREFIX) != new_by_ref[k]
    ]
    check("text matches legacy (prefix stripped)", not text_diffs, f"diffs: {text_diffs[:5]}")

    new_settings = json.loads(Path(args.new_settings).read_text(encoding="utf-8"))
    check("new settings is empty object", new_settings == {}, f"got: {new_settings!r}")

    print()
    if failures:
        print(f"{failures} check(s) failed")
        return 1
    print(f"all checks passed ({len(memories)} memories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())