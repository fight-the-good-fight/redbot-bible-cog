import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from bible.bible import Bible


class _EmptyNotes:
    async def __aenter__(self):
        return []

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _Config:
    def Notes(self):
        return _EmptyNotes()


def test_lookup_command_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_lookup(cog, ctx, message):
        calls.append((cog, ctx, message))

    monkeypatch.setattr(bible_module, "lookup_command", fake_lookup, raising=False)
    monkeypatch.setattr(bible_module, "has_translation", lambda message: False)
    monkeypatch.setattr(
        bible_module,
        "get_book_info",
        lambda book, translation="akjv": {
            "book": "genesis",
            "filename": "akjv/genesis.json",
            "extras": ["Authorized (King James) Version (AKJV)"],
            "matched": {"name": "Genesis"},
        },
    )
    monkeypatch.setattr(bible_module, "bundled_data_path", lambda self: str(Path(__file__).resolve().parents[1] / "data"))

    cog = Bible(SimpleNamespace())
    cog.config = _Config()
    ctx = SimpleNamespace(send=lambda *args, **kwargs: None)

    asyncio.run(Bible.__dict__["lookup"].callback(cog, ctx, message="Genesis 1:1"))

    assert calls == [(cog, ctx, "Genesis 1:1")]


def test_lookup_command_smoke(monkeypatch, tmp_path):
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

    captures = {}

    async def fake_menu(ctx, embeds, controls=None, timeout=None):
        captures["ctx"] = ctx
        captures["embeds"] = embeds
        captures["controls"] = controls
        captures["timeout"] = timeout

    monkeypatch.setattr(lookup_module, "menu", fake_menu)
    monkeypatch.setattr(lookup_module, "bundled_data_path", lambda cog: str(tmp_path))

    cog = SimpleNamespace(config=_Config())
    ctx = SimpleNamespace(send=lambda *args, **kwargs: None)

    asyncio.run(lookup_module.lookup(cog, ctx, "Genesis 1:1"))

    assert captures["timeout"] == 30
    assert captures["embeds"][0].title == "Genesis 1:1 - Authorized (King James) Version (AKJV)"
    assert "[1] In the beginning" in captures["embeds"][0].description
