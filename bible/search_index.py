import json
import sqlite3
from pathlib import Path
from typing import Iterable


CREATE_VERSES_SQL = """
create table if not exists verses (
    translation text not null,
    book text not null,
    chapter integer not null,
    verse integer not null,
    text text not null,
    normalized_text text not null,
    source_file text not null
)
"""

CREATE_INDEXES_SQL = [
    "create index if not exists idx_verses_normalized_text on verses(normalized_text)",
    "create index if not exists idx_verses_reference on verses(translation, book, chapter, verse)",
]


def _normalize_query(query: str) -> str:
    return query.lower()


def _book_display_name(book: str | dict) -> str:
    if isinstance(book, str):
        return book
    for entry in book.get("meta", []):
        if isinstance(entry, dict) and "h" in entry:
            return entry["h"]
        if isinstance(entry, dict) and entry.get("toc2"):
            return entry["toc2"][0]
    return book.get("bookCode", "")


def _iter_verse_rows(source_dir: str) -> Iterable[tuple[str, str, int, int, str, str, str]]:
    base_path = Path(source_dir)
    for translation_dir in sorted(base_path.iterdir()):
        if not translation_dir.is_dir():
            continue
        translation = translation_dir.name
        for json_file in sorted(translation_dir.glob("*.json")):
            with json_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            book_name = _book_display_name(data["book"])
            for chapter in data["chapters"]:
                if "chapter" in chapter:
                    chapter_num = int(chapter["chapter"])
                    verses = chapter["verses"]
                    for verse in verses:
                        verse_num = int(verse["verse"])
                        verse_text = verse["text"]
                        yield (
                            translation,
                            book_name,
                            chapter_num,
                            verse_num,
                            verse_text,
                            _normalize_query(verse_text),
                            str(json_file),
                        )
                    continue

                chapter_num = int(chapter["chapterNumber"])
                verses = chapter["contents"]
                for verse in verses:
                    if "verseNumber" not in verse:
                        continue
                    verse_num = int(verse["verseNumber"])
                    verse_text = verse.get("verseText")
                    if verse_text is None:
                        continue
                    yield (
                        translation,
                        book_name,
                        chapter_num,
                        verse_num,
                        verse_text,
                        _normalize_query(verse_text),
                        str(json_file),
                    )


def build_search_index(source_dir: str, index_path: str) -> None:
    index_file = Path(index_path)
    index_file.parent.mkdir(parents=True, exist_ok=True)
    if index_file.exists():
        index_file.unlink()

    with sqlite3.connect(index_file) as conn:
        conn.execute(CREATE_VERSES_SQL)
        for statement in CREATE_INDEXES_SQL:
            conn.execute(statement)
        conn.executemany(
            """
            insert into verses
                (translation, book, chapter, verse, text, normalized_text, source_file)
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            list(_iter_verse_rows(source_dir)),
        )
        conn.commit()


def search_verses_sqlite(
    index_path: str,
    query: str,
    case_insensitive: bool = False,
    translation: str = "akjv",
) -> list[dict[str, object]]:
    normalized_query = _normalize_query(query)
    if case_insensitive:
        sql = """
            select book, chapter, verse, text
            from verses
            where translation = ? and instr(normalized_text, ?) > 0
            order by book, chapter, verse
        """
        pattern = normalized_query
    else:
        sql = """
            select book, chapter, verse, text
            from verses
            where translation = ? and instr(text, ?) > 0
            order by book, chapter, verse
        """
        pattern = query

    with sqlite3.connect(f"file:{index_path}?mode=ro", uri=True) as conn:
        rows = conn.execute(sql, (translation, pattern)).fetchall()
    return [
        {"book": row[0], "chapter": row[1], "verse": row[2], "text": row[3]}
        for row in rows
    ]


def search_verses_files(
    source_dir: str,
    query: str,
    case_insensitive: bool = False,
    translation: str = "akjv",
) -> list[dict[str, object]]:
    query_value = _normalize_query(query) if case_insensitive else query
    results: list[dict[str, object]] = []
    translation_dir = Path(source_dir) / translation
    for json_file in sorted(translation_dir.glob("*.json")):
        with json_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
        book_name = data["book"]
        for chapter in data["chapters"]:
            chapter_num = chapter["chapter"]
            for verse in chapter["verses"]:
                verse_text = verse["text"]
                haystack = _normalize_query(verse_text) if case_insensitive else verse_text
                if query_value in haystack:
                    results.append(
                        {
                            "book": book_name,
                            "chapter": chapter_num,
                            "verse": verse["verse"],
                            "text": verse_text,
                        }
                    )
    return results
