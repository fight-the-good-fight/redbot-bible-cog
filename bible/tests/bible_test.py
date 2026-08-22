from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import asyncio
import pytest
from redbot.core import commands

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

    assert sent_messages == ["Bible cog version 1.2.1"]


def test_removeallnotes_denies_non_owner(monkeypatch):
    from bible import bible as bible_module

    cog = _make_cog()
    sent = []
    cleared = False

    def fake_save_memories(memories, path=None):
        nonlocal cleared
        cleared = True

    monkeypatch.setattr(bible_module, "save_memories", fake_save_memories)

    async def fake_is_owner(_author):
        return False

    async def fake_send(message):
        sent.append(message)

    cog.bot = SimpleNamespace(is_owner=fake_is_owner)
    ctx = SimpleNamespace(author=object(), send=fake_send)

    asyncio.run(Bible.__dict__["removeallnotes"].callback(cog, ctx))

    assert sent == ["Only the bot owner can use this command."]
    assert cleared is False


def test_removeallnotes_clears_and_confirms(monkeypatch):
    from bible import bible as bible_module

    cog = _make_cog()
    sent = []
    cleared = False

    def fake_save_memories(memories, path=None):
        nonlocal cleared
        cleared = True

    monkeypatch.setattr(bible_module, "save_memories", fake_save_memories)

    async def fake_is_owner(_author):
        return True

    async def fake_send(message):
        sent.append(message)

    cog.bot = SimpleNamespace(is_owner=fake_is_owner)
    ctx = SimpleNamespace(author=object(), send=fake_send)

    asyncio.run(Bible.__dict__["removeallnotes"].callback(cog, ctx))

    assert cleared is True
    assert sent == ["All notes removed"]


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


def test_markdownlint_is_pinned():
    makefile = Path(__file__).resolve().parents[2] / "Makefile"
    contents = makefile.read_text()
    assert "markdownlint-cli2@0.23.2" in contents


def test_memory_add_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_add(ctx, *, message):
        calls.append((ctx, message))

    monkeypatch.setattr(bible_module, "memory_add_command", fake_add)

    cog = _make_cog()
    ctx = SimpleNamespace()

    asyncio.run(Bible.__dict__["add"].callback(cog, ctx, message="Genesis 1:1 note"))

    assert calls == [(ctx, "Genesis 1:1 note")]


def test_memory_remove_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_remove(ctx, number):
        calls.append((ctx, number))

    monkeypatch.setattr(bible_module, "memory_remove_command", fake_remove)

    cog = _make_cog()
    ctx = SimpleNamespace()

    asyncio.run(Bible.__dict__["remove"].callback(cog, ctx, number=1))

    assert calls == [(ctx, 1)]


def test_memory_list_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_list(ctx, book=None, arg=None):
        calls.append((ctx, book, arg))

    monkeypatch.setattr(bible_module, "memory_list_command", fake_list)

    cog = _make_cog()
    ctx = SimpleNamespace()

    asyncio.run(Bible.__dict__["list"].callback(cog, ctx, book="Genesis", arg="1:1"))

    assert calls == [(ctx, "Genesis", "1:1")]


def test_bible_lookup_delegates(monkeypatch):
    from bible import bible as bible_module

    calls = []

    async def fake_lookup(cog, ctx, message):
        calls.append((cog, ctx, message))

    monkeypatch.setattr(bible_module, "lookup_command", fake_lookup)

    cog = _make_cog()
    ctx = SimpleNamespace()

    asyncio.run(Bible.__dict__["lookup"].callback(cog, ctx, message="Genesis 1:1"))

    assert calls == [(cog, ctx, "Genesis 1:1")]


def test_on_command_error_ignores_no_command():
    cog = _make_cog()
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(command=None, prefix="!", send=send)

    asyncio.run(cog.on_command_error(ctx, RuntimeError("boom")))

    assert sent == []


def test_on_command_error_ignores_other_cog():
    cog = _make_cog()
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(
        command=SimpleNamespace(cog=object()), prefix="!", send=send
    )

    asyncio.run(cog.on_command_error(ctx, RuntimeError("boom")))

    assert sent == []


def test_on_command_error_missing_required_argument():
    cog = _make_cog()
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(command=SimpleNamespace(cog=cog), prefix="!", send=send)
    error = commands.MissingRequiredArgument(
        SimpleNamespace(name="message", displayed_name="message")
    )

    asyncio.run(cog.on_command_error(ctx, error))

    assert sent[0].startswith("Missing required argument: `message`. Use `!help ")
    assert sent[0].endswith("` for usage.")


def test_on_command_error_bad_argument():
    cog = _make_cog()
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(command=SimpleNamespace(cog=cog), prefix="!", send=send)
    error = commands.BadArgument("boom")

    asyncio.run(cog.on_command_error(ctx, error))

    assert sent[0].startswith("Bad argument: `boom`. Use `!help ")
    assert sent[0].endswith("` for usage.")


def test_on_command_error_bad_argument_no_args():
    cog = _make_cog()
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(command=SimpleNamespace(cog=cog), prefix="!", send=send)
    error = commands.BadArgument()

    asyncio.run(cog.on_command_error(ctx, error))

    assert sent[0].startswith("Bad argument: `unknown`. Use `!help ")
    assert sent[0].endswith("` for usage.")


def test_on_command_error_reraises_other_errors():
    cog = _make_cog()

    ctx = SimpleNamespace(command=SimpleNamespace(cog=cog), prefix="!", send=None)

    with pytest.raises(RuntimeError):
        asyncio.run(cog.on_command_error(ctx, RuntimeError("boom")))


def test_cog_init_stores_bot():
    bot = SimpleNamespace()
    cog = Bible(bot)
    assert cog.bot is bot
