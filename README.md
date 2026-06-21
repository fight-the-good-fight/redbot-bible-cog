# Red-DiscordBot Bible Cog

A Red-DiscordBot cog for searching, reading, and noting Bible verses.

## Installation

1. Add this repository as a repo cog:
   ```
   .repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
   ```
2. Install and load:
   ```
   .cog install anvil bible
   .load bible
   ```

## Commands

### `bible translations`
Lists all supported Bible translations.

### `bible lookup <verse>`
Displays a chapter, specific verse, or verse range.
Examples:
- `bible lookup john 3:16` — single verse
- `bible lookup psalms 23` — entire chapter
- `bible lookup john 3:16-18` — verse range

### `bible search <text>`
Case-sensitive search for text across all books.

### `bible isearch <text>`
Case-insensitive search for text across all books.

### `memory add <verse> <note>`
Adds a personal note to a verse or chapter.
Examples:
- `memory add john 3:16 "God loved us first"`
- `memory add psalms 23 "This is my shepherd"`

### `memory remove <id>`
Removes a previously added note by its ID number.

### `memory list`
Lists all notes. Optionally filter by book (`memory list john`) or chapter/verse (`memory list john 3`).

### `removeallnotes`
Clears all stored notes (owner-only command).

## Data

The cog bundles three translations:
- **AKJV** — American King James Version (primary source)
- **ASV** — American Standard Version
- **BSB** — Berean Study Bible

All data is bundled locally; no external API calls are made.

## Notes Storage

User notes are stored in Redbot's `Config` system, keyed by the verse or chapter identifier. Notes persist across server restarts but are scoped to the guild where they were added.
