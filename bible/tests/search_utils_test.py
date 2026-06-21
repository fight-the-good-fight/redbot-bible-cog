from pathlib import Path

from bible.search_utils import (
    detect_translation,
    fix_book_name,
    get_book_extras_from_json,
    get_book_extras,
    get_book_info,
    get_verse_offset,
    has_translation,
    match_book,
)


def test_detect_translation_and_has_translation():
    assert detect_translation("Genesis 1:1 kjv") == "akjv"
    assert detect_translation("Genesis 1:1 asv") == "asv"
    assert detect_translation("Genesis 1:1 bsb") == "bsb"
    assert detect_translation("Genesis 1:1") is None

    assert has_translation("Genesis 1:1 kjv") is True
    assert has_translation("Genesis 1:1") is False


def test_detect_translation_edge_cases():
    # Case insensitivity
    assert detect_translation("genesis 1:1 AKJV") == "akjv"
    assert detect_translation("genesis 1:1 Asv") == "asv"
    assert detect_translation("genesis 1:1 BSB") == "bsb"
    assert detect_translation("genesis 1:1 KJV") == "akjv"

    # Translation at different positions (leading translation now supported)
    assert detect_translation("kjv genesis 1:1") == "akjv"
    # "in kjv" still matches trailing "kjv" — ambiguous but expected behavior
    assert detect_translation("genesis 1:1 in kjv") == "akjv"
    # "1 kjv" matches trailing "kjv" — expected behavior
    assert detect_translation("1 kjv") == "akjv"


def test_fix_book_name_and_match_book():
    assert fix_book_name(" Psalm ") == "psalms"
    assert fix_book_name("Revelations") == "revelation"
    assert fix_book_name("Song of Songs") == "songofsolomon"

    assert match_book("genesis") == {"name": "Genesis", "order": 1}
    assert match_book("enoch") == {"name": "Enoch", "order": 67}
    assert match_book("doesnotexist") is None


def test_match_book_edge_cases():
    # OT book
    assert match_book("leviticus") == {"name": "Leviticus", "order": 3}
    assert match_book("deuteronomy") == {"name": "Deuteronomy", "order": 5}

    # NT book
    assert match_book("luke") == {"name": "Luke", "order": 42}
    assert match_book("acts") == {"name": "Acts", "order": 44}

    # Apocrypha book
    assert match_book("enoch") == {"name": "Enoch", "order": 67}
    assert match_book("jude") == {"name": "Jude", "order": 65}

    # Invalid
    assert match_book("z") is None
    assert match_book("") is None


def test_get_verse_offset():
    # Verse numbers present
    assert get_verse_offset([{"text": "intro"}, {"verseNumber": "1"}, {"verseNumber": "2"}]) == 1
    assert get_verse_offset([{"verseNumber": "1"}, {"verseNumber": "2"}]) == 0

    # No verse numbers
    assert get_verse_offset([{"text": "intro"}, {"text": "verse one"}]) == 0
    assert get_verse_offset([]) == 0


def test_get_book_info_smoke():
    book_info = get_book_info("Genesis")
    assert book_info is not None
    assert book_info["book"] == "genesis"
    assert book_info["filename"] == "akjv/genesis.json"
    assert book_info["matched"]["name"] == "Genesis"


def test_get_book_extras_from_json_smoke():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    book_info = get_book_info("exodus")
    assert book_info is not None

    extras = get_book_extras_from_json(str(data_dir), book_info, "akjv")

    assert extras[0] == "Authorized (King James) Version (AKJV)"


def test_get_book_extras():
    # OT book
    assert get_book_extras({"name": "Genesis", "order": 1}, "akjv") == ["Authorized (King James) Version (AKJV)"]

    # NT book
    assert get_book_extras({"name": "Luke", "order": 42}, "akjv") == ["Authorized (King James) Version (AKJV)"]

    # Apocrypha book
    assert get_book_extras({"name": "Enoch", "order": 67}, "akjv") == ["Apocrypha"]


def test_get_book_extras_from_json_edge_cases():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    book_info = get_book_info("exodus")
    assert book_info is not None

    # Non-string book name (e.g., from a non-string JSON entry)
    book_info_with_dict_book = book_info.copy()
    book_info_with_dict_book["book"] = {"name": "Exodus", "description": "test"}
    extras = get_book_extras_from_json(str(data_dir), book_info_with_dict_book, "akjv")
    assert extras == []  # match_book can't handle dict, returns []

    # Missing data (shouldn't crash)
    book_info_missing = book_info.copy()
    book_info_missing.pop("book", None)
    extras = get_book_extras_from_json(str(data_dir), book_info_missing, "akjv")
    assert extras == []  # Should return empty list

    # Invalid translation
    book_info = get_book_info("exodus")
    extras = get_book_extras_from_json(str(data_dir), book_info, "invalid_translation")
    assert extras == []  # Should return empty list
