#!/usr/bin/env python3
"""
Migrate memories from a dart-app backup into the new cog's memories.json.

The new cog stores memories in a dedicated memories.json file (a plain JSON
list of {number, book, chapter, verse, note}) and no longer uses the Redbot
Config, so the new settings.json is an empty object.

Usage:
    python scripts/migrate_memories.py
    python scripts/migrate_memories.py --backup ... --settings ... --out-dir ...

Outputs (refuses to overwrite without --force):
    <out-dir>/new-memories.json
    <out-dir>/new-settings.json
"""

import argparse
import json
import sys
from pathlib import Path

# dart-app book keys that do not match the cog's normalized book names
BOOK_NAME_MAP = {
    "1Enoch": "Enoch",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def extract_notes(backup: dict) -> list[dict]:
    """Collect dart-app commentary entries that carry note text.

    Entries with only highlights/hashtags and no text are not memories and
    are skipped.
    """
    notes = []
    for book, items in backup.get("commentaries", {}).items():
        for item in items:
            text = item.get("text") or ""
            if not text.strip():
                continue
            notes.append(
                {
                    "book": BOOK_NAME_MAP.get(book, book),
                    "chapter": item["chapter"],
                    "verse": item["verse"],
                    "note": text,
                }
            )
    return notes


def order_notes(notes: list[dict], legacy_notes: list[dict]) -> tuple[list[dict], list[dict]]:
    """Order notes to match the legacy settings order.

    Returns (ordered, leftover) where leftover are dart notes with no
    matching legacy note, sorted by (book, chapter, verse).
    """
    by_ref = {(n["book"], n["chapter"], n["verse"]): n for n in notes}
    ordered = []
    matched = set()
    for legacy in legacy_notes:
        key = (
            BOOK_NAME_MAP.get(legacy["book"], legacy["book"]),
            legacy["chapter"],
            legacy["verse"],
        )
        if key in by_ref:
            ordered.append(by_ref[key])
            matched.add(key)
    leftover = sorted(
        (n for n in notes if (n["book"], n["chapter"], n["verse"]) not in matched),
        key=lambda n: (n["book"], n["chapter"], n["verse"]),
    )
    return ordered, leftover


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate dart-app commentaries into the new cog's memories.json"
    )
    parser.add_argument(
        "--backup",
        default="data-live/dart-app-backup.json",
        help="dart-app backup JSON (default: %(default)s)",
    )
    parser.add_argument(
        "--settings",
        default="data-live/settings.json",
        help="legacy cog settings.json, used for note ordering (default: %(default)s)",
    )
    parser.add_argument(
        "--out-dir",
        default="data-live",
        help="output directory (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing output files",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    memories_path = out_dir / "new-memories.json"
    new_settings_path = out_dir / "new-settings.json"

    for path in (memories_path, new_settings_path):
        if path.exists() and not args.force:
            sys.exit(f"error: {path} already exists (use --force to overwrite)")

    backup = load_json(Path(args.backup))
    legacy = load_json(Path(args.settings))
    legacy_notes = []
    for data in legacy.values():
        legacy_notes.extend(data.get("GLOBAL", {}).get("Notes", []))

    notes = extract_notes(backup)
    ordered, leftover = order_notes(notes, legacy_notes)
    matched_count = len(ordered) - len(leftover)

    memories = [
        {
            "number": i,
            "book": n["book"],
            "chapter": n["chapter"],
            "verse": n["verse"],
            "note": n["note"],
        }
        for i, n in enumerate(ordered, start=1)
    ]

    out_dir.mkdir(parents=True, exist_ok=True)
    memories_path.write_text(json.dumps(memories, indent=2) + "\n", encoding="utf-8")
    new_settings_path.write_text("{}\n", encoding="utf-8")

    print(f"migrated {len(memories)} memories -> {memories_path}")
    print(f"wrote empty settings -> {new_settings_path}")
    if leftover:
        print(f"warning: {len(leftover)} dart notes not in legacy settings, appended at end")
    if len(legacy_notes) > matched_count:
        print(
            f"warning: {len(legacy_notes) - matched_count} legacy notes have no dart commentary text"
        )


if __name__ == "__main__":
    main()