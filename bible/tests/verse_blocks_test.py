from bible.verse_blocks import (
    VERSE_BLOCKS,
    block_changes,
    block_memories,
    block_verse_meta,
    block_verse_text,
    render_chapter_lines,
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


def test_block_verse_text_emphasizes_changed_from():
    verse = {
        "verse": 1,
        "text": "In the beginning God created the heaven and the earth.",
    }
    change = {
        "ID": 1,
        "BCV": "Genesis 1:1",
        "verse": 1,
        "memorySummary": {"changedFrom": "heaven", "changedTo": "heavens"},
    }
    ctx = _ctx(changes={"1": [change]})
    assert block_verse_text(verse, ctx) == [
        "**[1] In the beginning God created the *heaven* and the earth.**"
    ]


def test_block_verse_text_no_emphasis_when_changed_from_empty():
    verse = {"verse": 1, "text": "In the beginning"}
    change = {
        "ID": 1,
        "BCV": "Genesis 1:1",
        "verse": 1,
        "memorySummary": {"changedFrom": "", "changedTo": "heavens"},
    }
    ctx = _ctx(changes={"1": [change]})
    assert block_verse_text(verse, ctx) == ["**[1] In the beginning**"]


def test_block_verse_text_no_emphasis_when_word_absent():
    verse = {"verse": 1, "text": "In the beginning"}
    change = {
        "ID": 1,
        "BCV": "Genesis 1:1",
        "verse": 1,
        "memorySummary": {"changedFrom": "zebra", "changedTo": "horse"},
    }
    ctx = _ctx(changes={"1": [change]})
    assert block_verse_text(verse, ctx) == ["**[1] In the beginning**"]


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
    assert lines[2] == "> **Memories:**"
    assert lines[3] == "> - a note"
    assert lines[4] == ">"
    assert lines[5] == "> **Change recorded for Genesis 1:1 (KJV):**"


def test_render_verse_lines_skips_empty_blocks():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(notes={"1": ["a note"]})
    lines = render_verse_lines(verse, ctx)
    assert lines == ["**[1] In the beginning**", "", "> **Memories:**", "> - a note"]


def test_verse_blocks_order_is_verse_meta():
    assert VERSE_BLOCKS == [block_verse_text, block_verse_meta]


def test_block_verse_meta_none_when_no_meta():
    verse = {"verse": 1, "text": "In the beginning"}
    assert block_verse_meta(verse, _ctx()) is None


def test_block_verse_meta_memories_only():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(notes={"1": ["a note"]})
    assert block_verse_meta(verse, ctx) == ["> **Memories:**", "> - a note"]


def test_block_verse_meta_changes_only():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(changes={"1": [{"ID": 1, "BCV": "Genesis 1:1", "verse": 1}]})
    lines = block_verse_meta(verse, ctx)
    assert lines[0] == "> **Change recorded for Genesis 1:1 (KJV):**"
    assert lines[-1] == "> https://search.thesupernaturalbiblechanges.com/changes/1"


def test_block_verse_meta_combines_memories_and_changes():
    verse = {"verse": 1, "text": "In the beginning"}
    ctx = _ctx(
        notes={"1": ["a note"]},
        changes={"1": [{"ID": 1, "BCV": "Genesis 1:1", "verse": 1}]},
    )
    assert block_verse_meta(verse, ctx) == [
        "> **Memories:**",
        "> - a note",
        ">",
        "> **Change recorded for Genesis 1:1 (KJV):**",
        "> https://search.thesupernaturalbiblechanges.com/changes/1",
    ]


def test_render_chapter_lines_no_blank_line_without_meta():
    verses = [
        {"verse": 1, "text": "Verse 1"},
        {"verse": 2, "text": "Verse 2"},
    ]
    assert render_chapter_lines(verses, _ctx()) == [
        "**[1] Verse 1**",
        "**[2] Verse 2**",
    ]


def test_render_chapter_lines_blank_line_after_meta_verse():
    verses = [
        {"verse": 1, "text": "Verse 1"},
        {"verse": 2, "text": "Verse 2"},
    ]
    ctx = _ctx(notes={"1": ["a note"]})
    assert render_chapter_lines(verses, ctx) == [
        "**[1] Verse 1**",
        "",
        "> **Memories:**",
        "> - a note",
        "",
        "**[2] Verse 2**",
    ]


def test_render_chapter_lines_no_trailing_blank_line():
    verses = [
        {"verse": 1, "text": "Verse 1"},
        {"verse": 2, "text": "Verse 2"},
    ]
    ctx = _ctx(notes={"2": ["a note"]})
    assert render_chapter_lines(verses, ctx) == [
        "**[1] Verse 1**",
        "**[2] Verse 2**",
        "",
        "> **Memories:**",
        "> - a note",
    ]