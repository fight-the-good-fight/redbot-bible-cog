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