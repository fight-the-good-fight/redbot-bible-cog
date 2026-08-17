from typing import cast

import asyncio
import json
from types import SimpleNamespace

from bible.bible import Bible


def _make_cog():
    return cast(Bible, Bible.__new__(Bible))


class _EmptyNotes:
    async def __aenter__(self):
        return []

    async def __aexit__(self, *_):
        return False


class _Config:
    def Notes(self):
        return _EmptyNotes()


async def _no_changes(_book_number, _chapter):
    return []


def test_lookup_command_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_lookup(_cog, _ctx, message):
        calls.append(message)

    monkeypatch.setattr(bible_module, "lookup_command", fake_lookup, raising=False)
    monkeypatch.setattr(bible_module, "has_translation", lambda _message: False)
    monkeypatch.setattr(
        bible_module,
        "get_book_info",
        lambda book, _translation="akjv": {
            "book": "genesis",
            "filename": "akjv/genesis.json",
            "extras": ["Authorized (King James) Version (AKJV)"],
            "matched": {"name": "Genesis"},
        },
    )

    cog = _make_cog()
    object.__setattr__(cog, "config", _Config())

    def _send(*_args, **_kwargs):
        return None

    ctx = SimpleNamespace(send=_send)

    asyncio.run(Bible.__dict__["lookup"].callback(cog, ctx, message="Genesis 1:1"))

    assert calls == ["Genesis 1:1"]


def test_lookup_command_renders_matching_notes(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    book_dir = tmp_path / "akjv"
    book_dir.mkdir()
    (book_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {
                        "chapter": 1,
                        "verses": [
                            {"verse": 1, "text": "In the beginning"},
                            {"verse": 2, "text": "And the earth"},
                        ],
                    }
                ],
            }
        )
    )

    class _Notes:
        async def __aenter__(self):
            return [
                {"book": "Genesis", "chapter": 1, "verse": 1, "note": "My note"},
                {"book": "Genesis", "chapter": 1, "verse": 3, "note": "Other"},
            ]

        async def __aexit__(self, *_):
            return False

    class _Config:
        def Notes(self):
            return _Notes()

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", _no_changes)

    cog = SimpleNamespace(config=_Config())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1"))

    description = captures["embeds"][0].description
    assert "[1] In the beginning" in description
    assert "My note" in description
    assert "Other" not in description



def test_lookup_command_does_not_duplicate_notes_across_verses(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    book_dir = tmp_path / "akjv"
    book_dir.mkdir()
    (book_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {
                        "chapter": 1,
                        "verses": [
                            {"verse": 1, "text": "In the beginning"},
                            {"verse": 2, "text": "And the earth"},
                        ],
                    }
                ],
            }
        )
    )

    class _Notes:
        async def __aenter__(self):
            return [{"book": "Genesis", "chapter": 1, "verse": 1, "note": "My note"}]

        async def __aexit__(self, *_):
            return False

    class _Config:
        def Notes(self):
            return _Notes()

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", _no_changes)

    cog = SimpleNamespace(config=_Config())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1-2"))

    description = captures["embeds"][0].description
    assert description.count("My note") == 1
    assert description.count("[1] In the beginning") == 1
    assert description.count("[2] And the earth") == 1


def _write_genesis(tmp_path, translation="akjv"):
    book_dir = tmp_path / translation
    book_dir.mkdir()
    (book_dir / "genesis.json").write_text(
        json.dumps(
            {
                "book": "genesis",
                "chapters": [
                    {
                        "chapter": 1,
                        "verses": [
                            {"verse": 1, "text": "In the beginning"},
                            {"verse": 2, "text": "And the earth"},
                        ],
                    }
                ],
            }
        )
    )


class _EmptyNotes:
    async def __aenter__(self):
        return []

    async def __aexit__(self, *_):
        return False


class _EmptyConfig:
    def Notes(self):
        return _EmptyNotes()


def test_lookup_command_renders_recorded_changes(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    _write_genesis(tmp_path)

    async def fake_get_changes(_book_number, _chapter):
        return [
            {
                "ID": 1,
                "BCV": "Genesis 1:1",
                "verse": 1,
                "changeType": "Other",
                "notes": "heaven is plural in Hebrew",
                "memorySummary": {
                    "restoredText": "In the beginning God created the heavens and the earth."
                },
            },
            {
                "ID": 2,
                "BCV": "Genesis 1:2",
                "verse": 2,
                "changeType": "Word",
                "notes": "moved and hovered are also changes",
                "memorySummary": {},
            },
        ]

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", fake_get_changes)

    cog = SimpleNamespace(config=_EmptyConfig())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1"))

    description = captures["embeds"][0].description
    assert "[1] In the beginning" in description
    assert "Change recorded for Genesis 1:1" in description
    assert "heaven is plural in Hebrew" in description
    assert "In the beginning God created the heavens and the earth." in description
    assert "Change recorded for Genesis 1:2" not in description


def test_lookup_command_renders_changes_for_verse_range(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    _write_genesis(tmp_path)

    async def fake_get_changes(_book_number, _chapter):
        return [
            {
                "ID": 1,
                "BCV": "Genesis 1:1",
                "verse": 1,
                "changeType": "Other",
                "notes": "heaven is plural in Hebrew",
                "memorySummary": {},
            },
            {
                "ID": 2,
                "BCV": "Genesis 1:2",
                "verse": 2,
                "changeType": "Word",
                "notes": "moved and hovered are also changes",
                "memorySummary": {},
            },
        ]

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", fake_get_changes)

    cog = SimpleNamespace(config=_EmptyConfig())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1-2"))

    description = captures["embeds"][0].description
    assert "Change recorded for Genesis 1:1" in description
    assert "Change recorded for Genesis 1:2" in description


def test_lookup_command_skips_changes_for_other_translations(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    _write_genesis(tmp_path, translation="asv")

    calls = []

    async def fake_get_changes(book_number, chapter):
        calls.append((book_number, chapter))
        return []

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", fake_get_changes)

    cog = SimpleNamespace(config=_EmptyConfig())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1 asv"))

    assert calls == []
    assert "Change recorded" not in captures["embeds"][0].description


def test_lookup_command_skips_changes_for_chapter_lookup(monkeypatch, tmp_path):
    lookup_module = __import__("bible.lookup_command", fromlist=["lookup"])

    _write_genesis(tmp_path)

    calls = []

    async def fake_get_changes(book_number, chapter):
        calls.append((book_number, chapter))
        return []

    captures = {}

    async def fake_menu(_ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda _cog: str(tmp_path))
    monkeypatch.setattr(lookup_module, "get_changes_for_chapter", fake_get_changes)

    cog = SimpleNamespace(config=_EmptyConfig())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1"))

    assert calls == []
    assert "Change recorded" not in captures["embeds"][0].description

