import asyncio
from types import SimpleNamespace

from bible import memory_command


def _store(notes):
    """Return (load, save) fakes that operate on the shared notes list."""

    def load(path=None):
        return notes

    def save(memories, path=None):
        notes[:] = memories

    return load, save


def test_add_memory_note_smoke(monkeypatch):
    notes = []
    sent = []
    load, save = _store(notes)

    monkeypatch.setattr(
        memory_command,
        "get_book_info",
        lambda book, translation="akjv": {"matched": {"name": "Genesis"}},
    )
    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(memory_command, "save_memories", save)

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.add(ctx, message="Genesis 1:1 note text"))

    assert notes == [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}
    ]
    assert sent == ["Note added for Genesis 1:1"]


def test_remove_memory_note_smoke(monkeypatch):
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}
    ]
    sent = []
    load, save = _store(notes)

    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(memory_command, "save_memories", save)

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.remove(ctx, number=1))

    assert notes == []
    assert sent == ["Note removed"]


def test_list_memory_notes_smoke(monkeypatch):
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}
    ]
    captures = {}
    load, _ = _store(notes)

    async def fake_menu(ctx, embeds, controls=None, timeout=None):
        captures["ctx"] = ctx
        captures["embeds"] = embeds
        captures["controls"] = controls
        captures["timeout"] = timeout

    monkeypatch.setattr(memory_command, "menu", fake_menu)
    monkeypatch.setattr(memory_command, "load_memories", load)

    async def send(message):
        captures.setdefault("sent", []).append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.list(ctx))

    assert captures["timeout"] == 30
    assert captures["embeds"][0].title == "Memory"
    assert "note text" in captures["embeds"][0].description


def test_add_invalid_argument():
    sent = []

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.add(ctx, message="no reference here"))

    assert sent == ["Invalid argument: no reference here"]


def test_add_book_not_found(monkeypatch):
    notes = []
    sent = []
    load, save = _store(notes)

    monkeypatch.setattr(
        memory_command, "get_book_info", lambda book, translation="akjv": None
    )
    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(memory_command, "save_memories", save)

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.add(ctx, message="Bogus 1:1 note text"))

    assert notes == []
    assert sent == ["Book not found: Bogus"]


def test_remove_note_not_found(monkeypatch):
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}
    ]
    sent = []
    load, save = _store(notes)

    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(memory_command, "save_memories", save)

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.remove(ctx, number=5))

    assert len(notes) == 1
    assert sent == ["Note not found"]


def test_remove_renumbers_remaining_notes(monkeypatch):
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "first"},
        {"number": 2, "book": "Genesis", "chapter": 2, "verse": 1, "note": "second"},
    ]
    sent = []
    load, save = _store(notes)

    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(memory_command, "save_memories", save)

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.remove(ctx, number=1))

    assert notes == [
        {"number": 1, "book": "Genesis", "chapter": 2, "verse": 1, "note": "second"}
    ]
    assert sent == ["Note removed"]


def test_list_book_not_found(monkeypatch):
    sent = []

    monkeypatch.setattr(
        memory_command, "get_book_info", lambda book, translation="akjv": None
    )

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.list(ctx, book="Bogus"))

    assert sent == ["Book not found: Bogus"]


def test_list_filtered_by_book_and_verse(monkeypatch):
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "target"},
        {"number": 2, "book": "Exodus", "chapter": 1, "verse": 1, "note": "wrong book"},
        {"number": 3, "book": "Genesis", "chapter": 2, "verse": 1, "note": "wrong chapter"},
        {"number": 4, "book": "Genesis", "chapter": 1, "verse": 2, "note": "wrong verse"},
    ]
    captures = {}
    load, _ = _store(notes)

    async def fake_menu(ctx, embeds, controls=None, timeout=None):
        captures["embeds"] = embeds

    monkeypatch.setattr(memory_command, "menu", fake_menu)
    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(
        memory_command,
        "get_book_info",
        lambda book, translation="akjv": {"matched": {"name": "Genesis"}},
    )

    async def send(message):
        captures.setdefault("sent", []).append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.list(ctx, book="Genesis", arg="1:1"))

    description = captures["embeds"][0].description
    assert "target" in description
    assert "wrong book" not in description
    assert "wrong chapter" not in description
    assert "wrong verse" not in description


def test_list_no_notes_found(monkeypatch):
    notes = [
        {"number": 1, "book": "Exodus", "chapter": 1, "verse": 1, "note": "other book"}
    ]
    sent = []
    load, _ = _store(notes)

    monkeypatch.setattr(memory_command, "load_memories", load)
    monkeypatch.setattr(
        memory_command,
        "get_book_info",
        lambda book, translation="akjv": {"matched": {"name": "Genesis"}},
    )

    async def send(message):
        sent.append(message)

    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.list(ctx, book="Genesis"))

    assert sent == ["No notes found"]