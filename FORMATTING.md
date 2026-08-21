# Discord Message Formatting

Reference for how the Bible cog formats its Discord responses — the templated
verse-lookup reply, embeds, links, color, and emphasis. Use this when redesigning
the lookup / notes / changes output.

Preview any change without Discord:

```bash
.venv/bin/python scripts/preview_lookup.py "Genesis 1:1"
```

Render a visual mockup of a hand-written description (iterates on look without
Discord):

```bash
.venv/bin/python scripts/render_mockup.py /tmp/mockup.html -o /tmp/mockup.png --scale 2
```

## How the lookup reply is built

The verse-lookup description is assembled from **ordered, pure block builders** in
`bible/verse_blocks.py`. Each block is a function `(verse, ctx) -> list[str] | None`:
it returns the description lines it contributes for one verse, or `None` to omit
itself (no data for this verse).

```python
# bible/verse_blocks.py
VERSE_BLOCKS = [block_verse_text, block_memories, block_changes]

def render_verse_lines(verse, ctx):
    out = []
    for block in VERSE_BLOCKS:
        lines = block(verse, ctx)
        if lines:
            if out:
                out.append("")   # blank line between non-empty blocks
            out.extend(lines)
    return out
```

Reorder `VERSE_BLOCKS` to reorder the reply; drop a block (or have it return
`None`) to omit its data. Blocks are pure over plain data, so they unit-test
without discord.py.

### The context (`ctx`)

`ctx` carries the per-chapter data collected **once** before rendering, in
`bible/lookup_command.py`:

- `notes_by_verse`: verse number (str) → list of raw note strings. Built from
  `load_memories()`, filtered to the chapter's verses (AKJV only).
- `changes_by_verse`: verse number (str) → list of raw change dicts. Built from
  the live `get_changes_for_chapter()` API, only for single-verse lookups
  (`have_chapter_and_verse`), AKJV only.

Keying by verse number (str) lets each block look up its own verse's data in O(1).

### The blocks

Two top-level blocks make up the reply. `block_memories` and `block_changes`
are the raw line producers that `block_verse_meta` combines into a blockquote.

| Block | Output | Omits when |
| --- | --- | --- |
| `block_verse_text` | `**[N] <verse text>**` — bold; any `changedFrom` word italicized in place | never (always contributes) |
| `block_verse_meta` | the verse's memories + changes as a single `> ` blockquote | no memories and no changes for the verse |

Raw producers (used by `block_verse_meta`, not in `VERSE_BLOCKS`):

| Producer | Output | Omits when |
| --- | --- | --- |
| `block_memories` | `**Memories:**` header + one `- ` bullet per note | no notes for the verse |
| `block_changes` | `format_change_lines(change)` per recorded change | no changes for the verse |

`block_verse_meta` joins the non-empty producers with a blank line, then quotes
every line (`> …`); the blank line becomes a bare `>` so it stays inside the
blockquote. This sets the meta apart from the verse text as clearly secondary.

`block_verse_text` emphasis: for each change on the verse it reads
`change["memorySummary"]["changedFrom"]` and, if non-empty, wraps the **first
occurrence** of that word in the verse text with `*…*` (italics). An empty/absent
`changedFrom`, or a word not present in the verse, leaves the text untouched.

### The change block (`format_change_lines`)

`bible/changes_api.py` — `format_change_lines(change)` builds plain description
lines for one recorded change, in order:

1. `**Change recorded for <BCV> (KJV):**`
2. `Notes:` + one `- ` bullet per non-empty line of `change["notes"]`
3. `**Possible Restoration:**` + `memorySummary["restoredText"]` (label on its own line)
4. `- changed: <changedFrom> to <changedTo>` (only if either is set; `?` fills a missing side)
5. The bare change-detail URL (auto-linked by Discord)

### Assembly and pagination

`bible/lookup_command.py` — after building `ctx`, all verses are rendered and
the lines joined:

```python
description = "\n".join(render_chapter_lines(verses, ctx))

for descript in pagify(description, page_length=3950, delims=["```", "\n\n"]):
    embed = discord.Embed(
        title=display_name + " " + chapter_verse + " - " + display_extras,
        description=descript,
        color=discord.Color.green(),
    )
    embeds.append(embed)
await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)
```

`render_chapter_lines` renders each verse via `render_verse_lines` and inserts a
blank line between two consecutive verses only when the preceding verse carries
meta, so its blockquote is separated from the next verse. Verses without meta
stay on consecutive lines.

### Why the description, not embed fields

Embed **fields** cap at 1024 chars each — too small for whole-chapter verse text.
The **description** caps at 4000 chars, and `pagify(..., page_length=3950, ...)`
splits long chapters into pages just under that. So the blocks emit description
lines, not field dicts. (The field-based `SECTIONS` pattern in `FORMATTING_ALT.md`
is the alternative; it fits short, field-shaped data, not long verse text.)

## Design decisions

- **Bold verse, not a heading.** Bold scales to whole chapters; a heading is too
  heavy for 30+ verses.
- **Meta in a blockquote.** Memories and changes are wrapped in a single `> `
  blockquote so they read as clearly secondary to the bold verse text; a blank
  line separates the blockquote from the next verse.
- **`Memories:` header + bullets.** Notes are user-typed free text (often
  `Commentary: ...`), so we don't parse a label out of them — we group them under
  a code-generated header instead.
- **Plain markdown, no `diff` boxes.** `box(..., lang="diff")` rendered notes and
  changes in monospace with red "deletion" coloring — the font mismatch that
  motivated this redesign.
- **`changedFrom` emphasized in the verse text.** The changed word is italicized
  where it appears in the verse, so it stands out in context.

## The rule that matters: you cannot color a word

Discord strips HTML and has no text-color markdown. There is no
`<span style="color:red">`. You have exactly **two** color levers:

1. The **embed accent bar** — one color per embed.
2. **`diff` code blocks** — per-line color via a leading `+` or `-`.

Everything else (bold, italics, underline, links) is standard markdown and does
not affect color. The current lookup output uses the accent bar (green) plus
plain markdown; `diff` boxes are available but no longer used.

## Lever 1 — the embed accent bar

Set on the `discord.Embed` in `bible/lookup_command.py`:

```python
embed = discord.Embed(
    title=verbose_title,
    description=descript,
    color=discord.Color.green(),   # <-- the bar color
)
```

Any color works:

```python
discord.Color.green()              # named preset
discord.Color.red()
discord.Color.from_str("#ff5500")  # hex string
discord.Color.rgb(255, 85, 0)      # r, g, b
0x2ecc71                           # raw int
```

## Lever 2 — `diff` code blocks (per-line color)

Wrap text in a `diff` fenced block and Discord colors each line by its first
character:

```diff
+ added line      -> green
- removed line    -> red
  context line    -> default (leading space)
```

Build these with Red's `box()` helper (`redbot.core.utils.chat_formatting`):

```python
from redbot.core.utils.chat_formatting import box

box("+ restored text", lang="diff")   # green line
box("- old text", lang="diff")        # red line
box("plain text")                     # no lang -> plain code block
```

Not used in the current lookup output (see Design decisions), but available if a
future redesign wants per-line color.

## Markdown reference (works in the embed description)

| Syntax | Result |
| --- | --- |
| `*text*` or `_text_` | italics |
| `**text**` | bold |
| `__text__` | underline |
| `***text***` | bold + italics |
| `~~text~~` | strikethrough |
| `` `text` `` | inline code |
| `[label](https://url)` | clickable link |
| `https://url` (bare) | auto-linked |
| `> text` | blockquote |
| `:fire:` | named emoji |

Spoiler: `||text||` — two pipes around the text.

A **code block** is a triple-backtick fence, optionally with a language tag for
syntax highlighting. `box(text, lang=...)` produces exactly this.

## Gotchas

- **Underscores collide.** Verse/field data contains underscores
  (`changed_from`, `changed_to`, `memorySummary`). Use `*italics*`, never
  `_italics_`, or the underscores in the data will break the formatting.
- **Markdown inside `box()` is literal.** A code block does not parse markdown.
  The current output avoids `box()` for the main reply, so all markdown is live.
- **Embed description limit is 4000 chars.** `pagify(..., page_length=3950, ...)`
  (`bible/lookup_command.py`) splits long chapters into pages just under that.
- **Bare URLs auto-link.** The change detail URL is sent bare and Discord links it.

## Where formatting happens

| Concern | File |
| --- | --- |
| Ordered block builders, `render_verse_lines`, `render_chapter_lines`, `VERSE_BLOCKS` | `bible/verse_blocks.py` |
| Change block lines: header, notes, restoration, changed, link | `bible/changes_api.py` — `format_change_lines()` |
| `ctx` assembly, verse loop, embed, color bar, pagination, menu | `bible/lookup_command.py` |
| Note add / remove / list text | `bible/memory_command.py` |
| `pagify` | `redbot.core.utils.chat_formatting` |
| `menu`, `DEFAULT_CONTROLS` | `redbot.core.utils.menus` |

## Recipes for redoing a response

- **Bold verse line**: `**[1] In the beginning...**`
- **Emphasize a word in the verse**: `*word*` (see `block_verse_text`)
- **Section header**: `**Memories:**`
- **Bullet list**: one `- item` per line
- **Safe italics**: `*text*`
- **Underline**: `__text__`
- **Link with custom text**: `[view change](https://search.thesupernaturalbiblechanges.com/changes/1)`
- **Link bare**: `https://search.thesupernaturalbiblechanges.com/changes/1`
- **Reorder the reply**: reorder `VERSE_BLOCKS` in `bible/verse_blocks.py`
- **Omit a section**: drop the block from `VERSE_BLOCKS`, or make it return `None`