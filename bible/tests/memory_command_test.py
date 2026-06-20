import asyncio
from types import SimpleNamespace

from bible import memory_command


class _MemoryNotes:
    def __init__(self, notes):
        self.notes = notes

    async def __aenter__(self):
        return self.notes

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _Config:
    def __init__(self, notes):
        self._notes = notes

    def Notes(self):
        return _MemoryNotes(self._notes)


def test_add_memory_note_smoke(monkeypatch):
    notes = []
    sent = []

    monkeypatch.setattr(memory_command, "get_book_info", lambda book, translation="akjv": {"matched": {"name": "Genesis"}})

    async def send(message):
        sent.append(message)

    cog = SimpleNamespace(config=_Config(notes))
    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.add(cog, ctx, message="Genesis 1:1 note text"))

    assert notes == [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}
    ]
    assert sent == ["Note added for Genesis 1:1"]


def test_remove_memory_note_smoke():
    notes = [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}]
    sent = []

    async def send(message):
        sent.append(message)

    cog = SimpleNamespace(config=_Config(notes))
    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.remove(cog, ctx, number=1))

    assert notes == []
    assert sent == ["Note removed"]


def test_list_memory_notes_smoke(monkeypatch):
    notes = [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "note text"}]
    captures = {}

    async def fake_menu(ctx, embeds, controls=None, timeout=None):
        captures["ctx"] = ctx
        captures["embeds"] = embeds
        captures["controls"] = controls
        captures["timeout"] = timeout

    monkeypatch.setattr(memory_command, "menu", fake_menu)

    async def send(message):
        captures.setdefault("sent", []).append(message)

    cog = SimpleNamespace(config=_Config(notes))
    ctx = SimpleNamespace(send=send)

    asyncio.run(memory_command.list(cog, ctx))

    assert captures["timeout"] == 30
    assert captures["embeds"][0].title == "Memory"
    assert "note text" in captures["embeds"][0].description
