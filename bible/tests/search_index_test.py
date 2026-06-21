from pathlib import Path

from bible.search_index import build_search_index, search_verses_files, search_verses_sqlite


def test_build_search_index_and_query(tmp_path: Path):
    index_path = tmp_path / "search.sqlite"
    build_search_index(str(Path(__file__).resolve().parents[1] / "data"), str(index_path))

    rows = search_verses_sqlite(str(index_path), "beginning")
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)


def test_case_insensitive_search_matches_uppercase(tmp_path: Path):
    index_path = tmp_path / "search.sqlite"
    build_search_index(str(Path(__file__).resolve().parents[1] / "data"), str(index_path))

    rows = search_verses_sqlite(str(index_path), "BEGINNING", case_insensitive=True)
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)


def test_search_files_helper_matches_sqlite_fixture():
    source_dir = str(Path(__file__).resolve().parents[1] / "data")
    rows = search_verses_files(source_dir, "beginning")
    assert rows
    assert any(row["book"] == "Genesis" for row in rows)
