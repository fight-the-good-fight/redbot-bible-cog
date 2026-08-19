# Scripts

Utility scripts for the Bible cog. Run them with the repo venv (`.venv/bin/python`).

## preview_lookup.py

Preview the reply the cog sends for a verse lookup, without Discord. It exercises the
real lookup pipeline — bundled verse data plus the live Supernatural Bible Changes API —
and prints the rendered embed (title, color, description). Use it to iterate on the
display format in `bible/lookup_command.py`: edit the format, re-run, see the result.

```bash
.venv/bin/python scripts/preview_lookup.py "Genesis 1:1"
```

Options:

| Flag | Effect |
| --- | --- |
| *(none)* | Verse + a sample note + the live change (if any). |
| `--no-notes` | Verse + change only (no note block). |
| `--memories PATH` | Load notes from a `memories.json` at `PATH` instead of the sample. |

Examples:

```bash
.venv/bin/python scripts/preview_lookup.py "John 3:16" --no-notes
.venv/bin/python scripts/preview_lookup.py "1Corinthians 13:13" --memories /path/to/memories.json
```

Sample output:

Default (verse + sample note + live change):

````text
=== Embed 1 of 1 ===
Title : Genesis 1:1 - Authorized (King James) Version (AKJV)
Color : #2ecc71
--- Description ---
[1] In the beginning God created the heaven and the earth.

```diff
- Sample note for Genesis 1:1 (display preview).
```

**Change recorded for Genesis 1:1 (KJV):**
```diff
Notes:
- The word "heaven" is plural in other translations of KJV, and is plural in Hebrew
Possible Restoration: In the beginning God created the heavens and the earth.
```
https://search.thesupernaturalbiblechanges.com/changes/1
--- End ---
````

`--no-notes` (verse + change only):

````text
=== Embed 1 of 1 ===
Title : Genesis 1:1 - Authorized (King James) Version (AKJV)
Color : #2ecc71
--- Description ---
[1] In the beginning God created the heaven and the earth.

**Change recorded for Genesis 1:1 (KJV):**
```diff
Notes:
- The word "heaven" is plural in other translations of KJV, and is plural in Hebrew
Possible Restoration: In the beginning God created the heavens and the earth.
```
https://search.thesupernaturalbiblechanges.com/changes/1
--- End ---
````

Change with no details (no notes, restoration, or word change — header + link only):

````text
=== Embed 1 of 1 ===
Title : 1 Corinthians 13:13 - Authorized (King James) Version (AKJV)
Color : #2ecc71
--- Description ---
[13] And now abideth faith, hope, charity, these three; but the greatest of these is charity.

```diff
- Sample note for 1Corinthians 13:13 (display preview).
```

**Change recorded for 1 Corinthians 13:13 (KJV):**
https://search.thesupernaturalbiblechanges.com/changes/47
--- End ---
````

Notes:

- The change block only appears for AKJV/KJV lookups with an explicit verse (book ≤ 66),
  matching the cog's gating.
- `--memories` expects a `memories.json` (a JSON array of note objects), not a
  `settings.json`.
- The script makes a live API call; it fails soft (no change block) if the API is
  unreachable.

## discord_mockup.html

A Discord dark-theme mockup of the current lookup embed — a hand-maintained HTML
render of what `preview_lookup.py` prints. It's a snapshot: after changing the
display in `bible/lookup_command.py` or `bible/changes_api.py`, re-sync it by hand.

How it's made (the actual loop):

1. Run the preview to get the current embed text:

   ```bash
   PYTHONPATH=. .venv/bin/python scripts/preview_lookup.py "Genesis 1:1"
   ```

2. Transcribe the output into the `.embed` section of this file:
   - the `.title` div ← the `Title :` line
   - one `<p>` per description line; verse lines are plain text, the
     `**Change recorded...**` header is `<strong>`
   - each `` ```diff `` box becomes a `<span class="codeblock">`; lines starting
     with a dash + space get `class="diff-minus"` (red), a plus + space would get
     `class="diff-plus"` (green), other lines stay uncolored (context)
   - the bare detail link becomes an `<a>`

3. Render it:

   ```bash
   .venv/bin/python scripts/render_mockup.py scripts/discord_mockup.html -o /tmp/preview.png --scale 2
   ```

4. Optional, for chat display: shrink it:

   ```bash
   sips --resampleWidth 596 /tmp/preview.png --out /tmp/preview_small.png
   ```

Current layout (Genesis 1:1, as of the changes-block reformat):

- Green embed (`#2ecc71`), title `<Book> <ref> - <translation name> (<key>)`.
- Description, in order:
  - Verse line: `[<verse>] <text>` per verse in the range.
  - Note block (AKJV only, per verse with notes): red diff box, one `- <note>` line per note.
  - Change block (AKJV only, explicit verse, book ≤ 66):
    - Bold `**Change recorded for <BCV> (KJV):**`
    - Diff box, only if there is anything to show:
      - `Notes:` header + one `- <note>` bullet per note
      - `Possible Restoration: <text>` when a restoration exists
      - `- changed: <from> to <to>` when word changes exist
    - Bare detail link `https://search.thesupernaturalbiblechanges.com/changes/<ID>`
      (a change with no notes/restoration/word change renders header + link only)

CSS classes: `.message` (the crop target), `.embed` (accent bar + background),
`.title`, `.codeblock` (monospace box), `.diff-minus` (red), `.diff-plus` (green).

## render_mockup.py

Render a Discord mockup HTML file to a tight-cropped PNG — the render half of the
preview loop. `preview_lookup.py` prints the text the cog will send; keep the mockup
HTML in sync with it, then render the HTML to an image to see how the display looks.
The script measures the `.message` box, sizes the viewport to it, and screenshots a
PNG with no grey margin.

```bash
.venv/bin/python scripts/render_mockup.py scripts/discord_mockup.html
```

Options:

| Flag | Effect |
| --- | --- |
| `-o, --output PATH` | Output PNG path (default: `<html>.png` next to the input). |
| `--selector CSS` | Content box to crop to (default: `.message`). |
| `--scale N` | Device scale factor for sharper output (default: `1.0`; `2` gives a 2x image). |
| `--browser NAME` | Browser to use: `chrome` (default, system Google Chrome) or `chromium`. |

Examples:

```bash
.venv/bin/python scripts/render_mockup.py scripts/discord_mockup.html -o /tmp/preview.png
.venv/bin/python scripts/render_mockup.py scripts/discord_mockup.html --scale 2
```

Notes:

- Dev-only dependency: `.venv/bin/python -m pip install playwright`. Not a cog runtime dep — do not add
  it to `bible/requirements.txt`.
- Uses the system Google Chrome by default (no browser download). If Chrome is not
  installed, run `playwright install chromium` and pass `--browser chromium`.
- The mockup lives at `scripts/discord_mockup.html` (committed); keep it in sync
  with the preview output — see the `discord_mockup.html` section above.

## migrate_memories.py

One-time migration that moves notes out of the cog's `settings.json` into a separate
`memories.json`, then clears `Notes` from `settings.json` so cog settings stay clean.

```bash
.venv/bin/python scripts/migrate_memories.py <path-to>/data/cogs/Bible/settings.json [memories.json]
```

- `memories.json` defaults to a sibling of the given `settings.json`.
- Refuses to overwrite an existing non-empty `memories.json`.
- Re-running on an already-migrated file reports nothing to migrate.
