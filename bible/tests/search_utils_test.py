from pathlib import Path

from bible.search_utils import (
    detect_translation,
    fix_book_name,
    get_book_extras_from_json,
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


def test_fix_book_name_and_match_book():
    assert fix_book_name(" Psalm ") == "psalms"
    assert fix_book_name("Revelations") == "revelation"
    assert fix_book_name("Song of Songs") == "songofsolomon"

    assert match_book("genesis") == {"name": "Genesis", "order": 1}
    assert match_book("enoch") == {"name": "Enoch", "order": 67}
    assert match_book("doesnotexist") is None


def test_get_verse_offset():
    assert get_verse_offset([{"text": "intro"}, {"verseNumber": "1"}, {"verseNumber": "2"}]) == 1
    assert get_verse_offset([{"verseNumber": "1"}, {"verseNumber": "2"}]) == 0


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
