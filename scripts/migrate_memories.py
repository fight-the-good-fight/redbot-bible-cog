#!/usr/bin/env python3
"""Migrate Bible memories from settings.json into a separate memories.json.

Usage:
    python scripts/migrate_memories.py <settings.json> [memories.json]

Reads the Notes array out of the cog's settings.json, writes it to a
memories.json file (a sibling of settings.json by default, or the path
given as the second argument), and clears Notes from settings.json so the
cog settings stay clean.

This is a one-time migration. Run it once after updating the cog to use
the separate memories store.
"""

import json
import sys
from pathlib import Path

MEMORIES_FILENAME = "memories.json"


def find_notes(data):
    """Return (identifier_key, global_scope, notes) for the first GLOBAL.Notes."""
    for ident, scopes in data.items():
        if isinstance(scopes, dict):
            global_scope = scopes.get("GLOBAL")
            if isinstance(global_scope, dict) and "Notes" in global_scope:
                return ident, global_scope, global_scope["Notes"]
    return None, None, None


def migrate(settings_path: Path, memories_path: Path) -> bool:
    """Move Notes from settings_path into memories_path.

    Returns True if a migration happened, False if there was nothing to do
    or the migration was refused.
    """
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    ident, global_scope, notes = find_notes(data)

    if ident is None:
        print("No Notes found in settings.json - nothing to migrate")
        return False

    if not notes:
        print("Notes is empty - nothing to migrate")
        return False

    if memories_path.exists():
        existing = json.loads(memories_path.read_text(encoding="utf-8"))
        if existing:
            print(
                f"Refusing to overwrite {memories_path} "
                f"(already has {len(existing)} notes)"
            )
            return False

    memories_path.write_text(json.dumps(notes, indent=2), encoding="utf-8")

    # Clear Notes from settings.json so the cog settings stay clean.
    del global_scope["Notes"]
    settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Migrated {len(notes)} notes to {memories_path}")
    print(f"Cleared Notes from {settings_path}")
    return True


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1

    settings_path = Path(argv[1])
    if not settings_path.exists():
        print(f"settings.json not found: {settings_path}")
        return 1

    if len(argv) > 2:
        memories_path = Path(argv[2])
    else:
        memories_path = settings_path.parent / MEMORIES_FILENAME

    return 0 if migrate(settings_path, memories_path) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))