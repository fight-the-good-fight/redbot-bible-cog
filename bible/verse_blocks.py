"""Ordered block builders for the verse lookup description.

Each block is a pure function ``(verse, ctx) -> list[str] | None``. It returns
the description lines it contributes for one verse, or ``None`` to omit itself
(no data for this verse). Reorder ``VERSE_BLOCKS`` to reorder the reply; drop a
block to omit its data.

The reply has two top-level blocks: the bold verse text, and the verse's meta
(memories + changes) rendered as a single Discord blockquote so it reads as
clearly secondary to the verse. ``block_memories`` and ``block_changes`` are
the raw line producers that ``block_verse_meta`` combines and quotes.

``ctx`` carries the per-chapter data collected once before rendering:

- ``notes_by_verse``: verse number (str) -> list of raw note strings
- ``changes_by_verse``: verse number (str) -> list of raw change dicts

Blocks are pure over plain data, so they unit-test without discord.py.
"""

from bible.changes_api import format_change_lines


def _verse_number(verse):
    """Return the verse number as a string, for both data shapes."""
    if "verseNumber" in verse:
        return str(verse["verseNumber"])
    return str(verse["verse"])


def _verse_text(verse):
    """Return the verse text, for both data shapes."""
    if "verseText" in verse:
        return verse["verseText"]
    return verse["text"]


def _emphasize_first(text, word):
    """Wrap the first occurrence of ``word`` in ``text`` with italics.

    Returns ``text`` unchanged when ``word`` is not present.
    """
    idx = text.find(word)
    if idx == -1:
        return text
    return text[:idx] + "*" + word + "*" + text[idx + len(word):]


def block_verse_text(verse, ctx):
    """The verse itself, bold so it stands out from the annotations.

    Any ``changedFrom`` word from a recorded change is emphasized (italic) in
    place so the changed word stands out within the verse. With no change, or
    an empty ``changedFrom``, the verse renders as-is.
    """
    number = _verse_number(verse)
    text = _verse_text(verse)
    for change in ctx["changes_by_verse"].get(number, []):
        changed_from = (change.get("memorySummary") or {}).get("changedFrom")
        if changed_from:
            text = _emphasize_first(text, str(changed_from))
    return [f"**[{number}] {text}**"]


def block_memories(verse, ctx):
    """User notes for this verse under a Memories: header, one bullet each."""
    notes = ctx["notes_by_verse"].get(_verse_number(verse), [])
    if not notes:
        return None
    lines = ["**Memories:**"]
    lines.extend(f"- {note}" for note in notes)
    return lines


def block_changes(verse, ctx):
    """Recorded changes for this verse, as plain description lines."""
    changes = ctx["changes_by_verse"].get(_verse_number(verse), [])
    if not changes:
        return None
    lines = []
    for change in changes:
        lines.extend(format_change_lines(change))
    return lines


def _quote(lines):
    """Prefix each line with ``> `` to form a Discord blockquote.

    A blank line becomes a bare ``>`` so it renders as a blank line *inside*
    the blockquote, keeping the quoted sections as one continuous quote.
    """
    return [f"> {line}" if line else ">" for line in lines]


def block_verse_meta(verse, ctx):
    """The verse's meta (memories + changes) as a single blockquote.

    Combines :func:`block_memories` and :func:`block_changes`, separating the
    two with a blank line, then quotes every line so the meta is set apart
    from the verse text. Returns ``None`` when the verse has no meta.
    """
    sections = [
        section
        for section in (block_memories(verse, ctx), block_changes(verse, ctx))
        if section
    ]
    if not sections:
        return None
    lines = []
    for i, section in enumerate(sections):
        if i > 0:
            lines.append("")
        lines.extend(section)
    return _quote(lines)


VERSE_BLOCKS = [block_verse_text, block_verse_meta]


def render_verse_lines(verse, ctx):
    """Render one verse's description lines from the ordered blocks.

    Non-empty blocks are separated by a blank line; a block returning ``None``
    is skipped. The verse text block always contributes, so the result is never
    empty.
    """
    out = []
    for block in VERSE_BLOCKS:
        lines = block(verse, ctx)
        if lines:
            if out:
                out.append("")
            out.extend(lines)
    return out


def render_chapter_lines(verses, ctx):
    """Render all verses' description lines for the lookup reply.

    Each verse is rendered via :func:`render_verse_lines`. A blank line is
    inserted between two consecutive verses only when the preceding verse
    carries meta (memories or changes), so its blockquote is visually
    separated from the next verse. Verses without meta stay on consecutive
    lines.
    """
    out = []
    for i, verse in enumerate(verses):
        if i > 0 and block_verse_meta(verses[i - 1], ctx) is not None:
            out.append("")
        out.extend(render_verse_lines(verse, ctx))
    return out