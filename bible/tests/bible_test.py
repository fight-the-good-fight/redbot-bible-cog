from typing import Any, cast

import asyncio
from pathlib import Path
from types import SimpleNamespace

from bible.bible import Bible, get_book_info
from bible.search_utils import get_book_extras_from_json


def _make_cog():
    return cast(Bible, Bible.__new__(Bible))


def test_translations_command_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_translations(ctx):
        calls.append(ctx)

    monkeypatch.setattr(bible_module, "translations_command", fake_translations)

    cog = _make_cog()
    ctx = SimpleNamespace()

    asyncio.run(Bible.__dict__["translations"].callback(cog, ctx))

    assert calls == [ctx]


def test_version_command_sends_version():
    cog = _make_cog()
    sent_messages = []

    async def fake_send(message):
        sent_messages.append(message)

    ctx = SimpleNamespace(send=fake_send)

    asyncio.run(Bible.__dict__["version"].callback(cog, ctx))

    assert sent_messages == ["Bible cog version 1.0.1"]


def test_search_command_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_search(ctx, arg):
        calls.append((ctx, arg))

    monkeypatch.setattr(bible_module, "search_command", fake_search)

    cog = _make_cog()
    ctx = SimpleNamespace(cog=SimpleNamespace())

    asyncio.run(Bible.__dict__["search"].callback(cog, ctx, arg="Genesis"))

    assert calls == [(ctx, "Genesis")]


def test_isearch_command_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_isearch(ctx, arg):
        calls.append((ctx, arg))

    monkeypatch.setattr(bible_module, "isearch_command", fake_isearch)

    cog = _make_cog()
    ctx = SimpleNamespace(cog=SimpleNamespace())

    asyncio.run(Bible.__dict__["isearch"].callback(cog, ctx, arg="Genesis"))

    assert calls == [(ctx, "Genesis")]


def test_get_book_info():
    book_info = cast(dict[str, Any], get_book_info("Genesis"))
    assert book_info["book"] == "genesis"
    assert book_info["filename"] == "akjv/genesis.json"
    assert book_info["matched"]["name"] == "Genesis"
    assert book_info["matched"]["order"] == 1
    assert book_info["extras"] == ["Authorized (King James) Version (AKJV)"]

    book_info = cast(dict[str, Any], get_book_info("genesis"))
    assert book_info["book"] == "genesis"
    assert book_info["filename"] == "akjv/genesis.json"
    assert book_info["matched"]["name"] == "Genesis"
    assert book_info["matched"]["order"] == 1
    assert book_info["extras"] == ["Authorized (King James) Version (AKJV)"]

    book_info = cast(dict[str, Any], get_book_info("Song of Solomon"))
    assert book_info["book"] == "songofsolomon"
    assert book_info["filename"] == "akjv/songofsolomon.json"
    assert book_info["matched"]["name"] == "Song of Solomon"
    assert book_info["matched"]["order"] == 22
    assert book_info["extras"] == ["Authorized (King James) Version (AKJV)"]

    book_info = cast(dict[str, Any], get_book_info("Song of Songs"))
    assert book_info["book"] == "songofsolomon"
    assert book_info["filename"] == "akjv/songofsolomon.json"
    assert book_info["matched"]["name"] == "Song of Solomon"
    assert book_info["matched"]["order"] == 22
    assert book_info["extras"] == ["Authorized (King James) Version (AKJV)"]

    book_info = get_book_info("invalid")
    assert book_info is None

    book_info = cast(dict[str, Any], get_book_info("enoch"))
    assert book_info["book"] == "enoch"
    assert book_info["filename"] == "akjv/enoch.json"
    assert book_info["matched"]["name"] == "Enoch"
    assert book_info["matched"]["order"] == 67
    assert book_info["extras"] == ["Apocrypha"]


def test_get_book_name_from_json():
    book_info = cast(dict[str, Any], get_book_info("exodus"))
    assert book_info["book"] == "exodus"
    book_extras = get_book_extras_from_json(
        str(Path(__file__).resolve().parents[1] / "data"), book_info, "akjv"
    )
    assert book_extras[0] == "Authorized (King James) Version (AKJV)"

    book_info = cast(dict[str, Any], get_book_info("exodus", "bsb"))
    assert book_info["filename"] == "bsb/exodus.json"
    book_extras = get_book_extras_from_json(
        str(Path(__file__).resolve().parents[1] / "data"), book_info, "bsb"
    )
    assert book_extras == ["- Berean Study Bible"]
