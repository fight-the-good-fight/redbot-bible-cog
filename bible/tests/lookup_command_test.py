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

    cog = SimpleNamespace(config=_Config())
    ctx = SimpleNamespace(send=lambda *_args, **_kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1"))

    description = captures["embeds"][0].description
    assert "[1] In the beginning" in description
    assert "My note" in description
    assert "Other" not in description


