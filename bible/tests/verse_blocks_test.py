from bible.verse_blocks import (
    VERSE_BLOCKS,
    block_changes,
    block_memories,
    block_verse_text,
    render_verse_lines,
)


def _ctx(notes=None, changes=None):
    return {
        "notes_by_verse": notes or {},
        "changes_by_verse": changes or {},
    }


def test_block_verse_text_bold_plain_shape():
    verse = {"verse": 1, "text": "In the beginning"}
    assert block_verse_text(verse, _ctx()) == ["**[1] In the beginning**"]


def test_block_verse_text_bold_usfm_shape():
    verse = {"verseNumber": "2", "verseText": "And the earth"}
    assert block_verse_text(verse, _ctx()) == ["**[2] And the earth**"]


def test_block_memories_none_when_no_notes():
    verse = {"verse": 1, "text": "In the beginning"}
    assert block_memories(verse, _ctx()) is None


def test_block_memories_header_and_bullets():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(notes={"1": ["Commentary: say heavens", "Another note"]})
    assert block_memories(verse, ctx) == [
        "**Memories:**",
        "- Commentary: say heavens",
        "- Another note",
    ]


def test_block_changes_none_when_no_changes():
    verse = {"verse": 1, "text": "In the beginning"}
    assert block_changes(verse, _ctx()) is None


def test_block_changes_formats_change_dicts():
    verse = {"verse": 1, "text": "In the beginning"}
    change = {"ID": 1, "BCV": "Genesis 1:1", "verse": 1}
    ctx = _ctx(changes={"1": [change]})
    lines = block_changes(verse, ctx)
    assert lines[0] == "**Change recorded for Genesis 1:1 (KJV):**"
    assert "https://search.thesupernaturalbiblechanges.com/changes/1" in lines


def test_render_verse_lines_verse_only():
    verse = {"verse": 1, "text": "In the beginning"}
    assert render_verse_lines(verse, _ctx()) == ["**[1] In the beginning**"]


def test_render_verse_lines_separates_blocks_with_blank_line():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(
        notes={"1": ["a note"]},
        changes={"1": [{"ID": 1, "BCV": "Genesis 1:1", "verse": 1}]},
    )
    lines = render_verse_lines(verse, ctx)
    assert lines[0] == "**[1] In the beginning**"
    assert lines[1] == ""
    assert lines[2] == "**Memories:**"
    assert lines[3] == "- a note"
    assert lines[4] == ""
    assert lines[5] == "**Change recorded for Genesis 1:1 (KJV):**"


def test_render_verse_lines_skips_empty_blocks():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(notes={"1": ["a note"]})
    lines = render_verse_lines(verse, ctx)
    assert lines == ["**[1] In the beginning**", "", "**Memories:**", "- a note"]


def test_verse_blocks_order_is_verse_memories_changes():
    assert VERSE_BLOCKS == [block_verse_text, block_memories, block_changes]