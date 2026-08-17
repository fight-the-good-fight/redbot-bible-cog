# Scripts

Utility scripts for the Bible cog. Run them with the repo venv (`.venv/bin/python`).

## preview_lookup.py

Preview the reply the cog sends for a verse lookup, without Discord. It exercises the
real lookup pipeline — bundled verse data plus the live Supernatural Bible Changes API —
and prints the rendered embed (title, color, description). Use it to iterate on the
display format in `bible/lookup_command.py`: edit the format, re-run, see the result.

```
.venv/bin/python scripts/preview_lookup.py "Genesis 1:1"
```

Options:

| Flag | Effect |
| --- | --- |
| *(none)* | Verse + a sample note + the live change (if any). |
| `--no-notes` | Verse + change only (no note block). |
| `--memories PATH` | Load notes from a `memories.json` at `PATH` instead of the sample. |

Examples:

```
.venv/bin/python scripts/preview_lookup.py "John 3:16" --no-notes
.venv/bin/python scripts/preview_lookup.py "1Corinthians 13:13" --memories /path/to/memories.json
```

Notes:
- The change block only appears for AKJV/KJV lookups with an explicit verse (book ≤ 66),
  matching the cog's gating.
- `--memories` expects a `memories.json` (a JSON array of note objects), not a
  `settings.json`.
- The script makes a live API call; it fails soft (no change block) if the API is
  unreachable.

## migrate_memories.py

One-time migration that moves notes out of the cog's `settings.json` into a separate
`memories.json`, then clears `Notes` from `settings.json` so cog settings stay clean.

```
.venv/bin/python scripts/migrate_memories.py <path-to>/data/cogs/Bible/settings.json [memories.json]
```

- `memories.json` defaults to a sibling of the given `settings.json`.
- Refuses to overwrite an existing non-empty `memories.json`.
- Re-running on an already-migrated file reports nothing to migrate.