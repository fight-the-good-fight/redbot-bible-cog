import json
from pathlib import Path

from bible.search_index import (
    _book_display_name,
    build_search_index,
    search_verses_files,
    search_verses_sqlite,
)


def test_build_search_index_and_query(tmp_path: Path):
    index_path = tmp_path / "search.sqlite"
    build_search_index(
        str(Path(__file__).resolve().parents[1] / "data"), str(index_path)
    )

    rows = search_verses_sqlite(str(index_path), "beginning")
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)


def test_case_insensitive_search_matches_uppercase(tmp_path: Path):
    index_path = tmp_path / "search.sqlite"
    build_search_index(
        str(Path(__file__).resolve().parents[1] / "data"), str(index_path)
    )

    rows = search_verses_sqlite(str(index_path), "BEGINNING", case_insensitive=True)
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)


def test_search_files_helper_matches_sqlite_fixture():
    source_dir = str(Path(__file__).resolve().parents[1] / "data")
    rows = search_verses_files(source_dir, "beginning")
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)


def test_book_display_name_toc2():
    book = {"meta": [{"toc2": ["Genesis"]}], "bookCode": "GEN"}
    assert _book_display_name(book) == "Genesis"


def test_book_display_name_book_code_fallback():
    book = {"meta": [], "bookCode": "GEN"}
    assert _book_display_name(book) == "GEN"


def test_build_search_index_skips_non_directory_entries(tmp_path: Path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "notes.txt").write_text("not a translation dir")
    translation_dir = source_dir / "akjv"
    translation_dir.mkdir()
    (translation_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {"chapter": 1, "verses": [{"verse": 1, "text": "beginning"}]}
                ],
            }
        )
    )

    index_path = tmp_path / "search.sqlite"
    build_search_index(str(source_dir), str(index_path))

    rows = search_verses_sqlite(str(index_path), "beginning")
    assert rows
    assert rows[0]["book"] == "genesis"


def test_build_search_index_skips_null_verse_text(tmp_path: Path):
    source_dir = tmp_path / "source"
    translation_dir = source_dir / "akjv"
    translation_dir.mkdir(parents=True)
    (translation_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {
                        "chapterNumber": "1",
                        "contents": [
                            {"p": None},
                            {"verseNumber": "1", "verseText": "the first verse"},
                            {"verseNumber": "2", "verseText": None},
                        ],
                    }
                ],
            }
        )
    )

    index_path = tmp_path / "search.sqlite"
    build_search_index(str(source_dir), str(index_path))

    rows = search_verses_sqlite(str(index_path), "first verse")
    assert len(rows) == 1
    assert rows[0]["verse"] == 1


def test_build_search_index_rebuilds_over_existing_index(tmp_path: Path):
    source_dir = tmp_path / "source"
    translation_dir = source_dir / "akjv"
    translation_dir.mkdir(parents=True)
    (translation_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {"chapter": 1, "verses": [{"verse": 1, "text": "beginning"}]}
                ],
            }
        )
    )

    index_path = tmp_path / "search.sqlite"
    build_search_index(str(source_dir), str(index_path))
    assert index_path.exists()
    build_search_index(str(source_dir), str(index_path))

    rows = search_verses_sqlite(str(index_path), "beginning")
    assert rows
    assert rows[0]["book"] == "genesis"
