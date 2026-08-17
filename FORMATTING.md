# Discord Message Formatting

Reference for how the Bible cog formats its Discord responses — embeds, links,
color, and emphasis. Use this when redesigning the lookup / notes / changes
output.

Preview any change without Discord:

```bash
.venv/bin/python scripts/preview_lookup.py "Genesis 1:1"
```

## The rule that matters: you cannot color a word

Discord strips HTML and has no text-color markdown. There is no
`<span style="color:red">`. You have exactly **two** color levers:

1. The **embed accent bar** — one color per embed.
2. **`diff` code blocks** — per-line color via a leading `+` or `-`.

Everything else (bold, italics, underline, links) is standard markdown and does
not affect color.

## Lever 1 — the embed accent bar

Set on the `discord.Embed` in `bible/lookup_command.py:175`:

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

Already in use:

- Notes render **red**: `bible/lookup_command.py:129` — `box("- " + note["note"], lang="diff")`
- Changes render **red**: `bible/changes_api.py:52` — `box("\n".join(detail_lines), lang="diff")`

To show a "restored" reading in green, start that line with `+` instead of `-`.

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
  The `**Change recorded for ...**` header (`bible/changes_api.py:32`) is
  *outside* the box, so it is bold; the `- type:` lines *inside* the diff box are
  colored but not markdown-parsed.
- **Embed description limit is 4000 chars.** `pagify(..., page_length=3950, ...)`
  (`bible/lookup_command.py:166`) splits long chapters into pages just under that.
- **Bare URLs auto-link.** The change detail URL is sent bare and Discord links it.

## Where formatting happens

| Concern | File |
| --- | --- |
| Verse + notes + changes assembly, embed, color bar, pagination, menu | `bible/lookup_command.py` |
| Change block: header, diff box, detail link | `bible/changes_api.py` — `format_change_lines()` |
| Note add / remove / list text | `bible/memory_command.py` |
| `box`, `pagify` | `redbot.core.utils.chat_formatting` |
| `menu`, `DEFAULT_CONTROLS` | `redbot.core.utils.menus` |

## Recipes for redoing a response

- **Bold heading** (outside any box): `**Genesis 1:1**`
- **Red "removed" line**: diff box, line starts with `-`
- **Green "restored" line**: diff box, line starts with `+`
- **Safe italics**: `*text*`
- **Underline**: `__text__`
- **Link with custom text**: `[view change](https://search.thesupernaturalbiblechanges.com/changes/1)`
- **Link bare**: `https://search.thesupernaturalbiblechanges.com/changes/1`
