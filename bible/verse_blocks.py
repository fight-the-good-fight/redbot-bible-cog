"""Ordered block builders for the verse lookup description.

Each block is a pure function ``(verse, ctx) -> list[str] | None``. It returns
the description lines it contributes for one verse, or ``None`` to omit itself
(no data for this verse). Reorder ``VERSE_BLOCKS`` to reorder the reply; drop a
block to omit its data.

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


VERSE_BLOCKS = [block_verse_text, block_memories, block_changes]


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