# Memories Migration Scripts

How to migrate memories from the dart-app backup and legacy cog settings
into the file format the current cog expects, and how to verify the result.

## Background

- The current cog stores memories in a dedicated `memories.json` file (a
  plain JSON list of `{number, book, chapter, verse, note}`) inside the
  cog's data directory. It no longer uses Redbot `Config` for notes.
- The legacy cog stored notes in `settings.json` under
  `<identifier>.GLOBAL.Notes`.
- The dart-app backup (`dart-app-backup.json`) holds the commentaries under
  `commentaries`: a map of book name to a list of
  `{chapter, verse, text, highlights, hashtags, updatedAt}` entries. Only
  entries with non-empty `text` are memories; highlight/hashtag-only
  entries are skipped.

## Files

| File | Purpose |
|---|---|
| `scripts/migrate_memories.py` | Produces `new-memories.json` + `new-settings.json` |
| `scripts/verify_migration.py` | Checks the produced files against the cog code |
| `data-live/dart-app-backup.json` | Source: dart-app commentaries |
| `data-live/settings.json` | Source: legacy cog settings (note order + cross-check) |
| `data-live/new-memories.json` | Output: memories for the new cog |
| `data-live/new-settings.json` | Output: empty settings (`{}`) |

## Prerequisites

Both scripts need the repo venv (the verify script imports the cog):

```bash
uv venv .venv -p 3.11
uv pip install -r bible/requirements.txt pip --python .venv/bin/python
```

## 1. Run the migration

```bash
.venv/bin/python scripts/migrate_memories.py
```

Defaults:

| Flag | Default |
|---|---|
| `--backup` | `data-live/dart-app-backup.json` |
| `--settings` | `data-live/settings.json` |
| `--out-dir` | `data-live` |

Outputs `new-memories.json` and `new-settings.json` in `--out-dir`. The
script refuses to overwrite existing outputs; pass `--force` to
regenerate. Source files are never modified.

Custom paths:

```bash
.venv/bin/python scripts/migrate_memories.py \
  --backup /path/to/dart-app-backup.json \
  --settings /path/to/settings.json \
  --out-dir /path/to/output
```

## 2. Verify

```bash
.venv/bin/python scripts/verify_migration.py
```

Flags: `--memories`, `--settings`, `--new-settings` (defaults point at the
`data-live/` outputs and sources). Exits 0 when all checks pass, 1
otherwise.

Checks performed:

- memories load through the cog's `memories_store`
- every note has exactly the keys `book, chapter, note, number, verse`
- every book resolves via `get_book_info`
- the lookup matching rule holds (`note["book"].lower() == book_name`)
- numbering is sequential 1..N
- the (book, chapter, verse) set matches the legacy settings
- note text matches the legacy settings after the `"Commentary: "` prefix
  strip
- the new settings file is `{}`

## 3. Install into the bot

Copy the outputs into the cog's data directory
(`<Red-DiscordBot data folder>/cogs/Bible/`):

- `new-memories.json` → `memories.json`
- `new-settings.json` → `settings.json` (optional; the cog reads no
  Config at all)

Then reload the cog (`.reload bible` or `.restart`).

## Migration rules

- Only dart entries with non-empty `text` become notes.
- Note text is the dart `text` verbatim (no `"Commentary: "` prefix).
- Book names: `1Enoch` is mapped to `Enoch` (the cog's apocryphal book
  67); all other dart book keys are used as-is. The mapping lives in
  `BOOK_NAME_MAP` in both scripts — keep them in sync if you add entries.
- Order: legacy settings order; dart notes missing from the legacy
  settings are appended at the end, sorted by (book, chapter, verse).
- Notes are renumbered 1..N.
- `new-settings.json` is always `{}`.

## Rerunning

The sources are never modified, so rerunning is safe:

```bash
.venv/bin/python scripts/migrate_memories.py --force
.venv/bin/python scripts/verify_migration.py
```

Rerun whenever the dart-app backup changes (new commentaries) or the
legacy settings change.

## Troubleshooting

- `ModuleNotFoundError: No module named 'redbot'` — you used the system
  python; use `.venv/bin/python`.
- `error: <file> already exists (use --force to overwrite)` — outputs
  exist; add `--force` to regenerate.
- `warning: N dart notes not in legacy settings, appended at end` — the
  backup has notes the legacy settings don't; they were appended.
- `warning: N legacy notes have no dart commentary text` — legacy notes
  with no matching dart entry were dropped; check the backup.