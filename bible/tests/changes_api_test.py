import asyncio

import aiohttp

from bible.changes_api import format_change_lines, get_changes_for_chapter


class _FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status = status
        self._payload = payload

    async def json(self, content_type=None):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False


class _FakeSession:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.posted = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    def post(self, url, json=None):
        self.posted.append((url, json))
        if self._error is not None:
            raise self._error
        return self._response


def _patch_session(monkeypatch, session):
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **_kwargs: session)


def test_get_changes_for_chapter_success(monkeypatch):
    changes = [{"ID": 1, "BCV": "Genesis 1:1", "verse": 1}]
    session = _FakeSession(response=_FakeResponse(200, changes))
    _patch_session(monkeypatch, session)

    result = asyncio.run(get_changes_for_chapter(1, 1))

    assert result == changes
    assert session.posted == [
        (
            "https://search.thesupernaturalbiblechanges.com/v1/GetChangesByChapter",
            {"bookNumber": 1, "chapterNumber": 1},
        )
    ]


def test_get_changes_for_chapter_http_error_returns_empty(monkeypatch):
    session = _FakeSession(response=_FakeResponse(500, "boom"))
    _patch_session(monkeypatch, session)

    assert asyncio.run(get_changes_for_chapter(1, 1)) == []


def test_get_changes_for_chapter_network_error_returns_empty(monkeypatch):
    session = _FakeSession(error=OSError("connection refused"))
    _patch_session(monkeypatch, session)

    assert asyncio.run(get_changes_for_chapter(1, 1)) == []


def test_get_changes_for_chapter_non_list_returns_empty(monkeypatch):
    session = _FakeSession(response=_FakeResponse(200, {"error": "bad"}))
    _patch_session(monkeypatch, session)

    assert asyncio.run(get_changes_for_chapter(1, 1)) == []


def test_format_change_lines_full():
    change = {
        "ID": 2,
        "BCV": "Genesis 1:2",
        "changeType": "Word",
        "notes": "moved and hovered are also changes",
        "memorySummary": {
            "restoredText": "and the earth was without form and void",
            "changedFrom": "",
            "changedTo": "",
            "notes": "Authorized King James Bible - 1845",
        },
    }

    lines = format_change_lines(change)

    assert lines[0] == "**Change recorded for Genesis 1:2 (KJV):**"
    joined = "\n".join(lines)
    assert "Notes:" in joined
    assert "- moved and hovered are also changes" in joined
    assert "Possible Restoration: and the earth was without form and void" in joined
    assert "type:" not in joined
    assert "Authorized King James Bible - 1845" not in joined
    assert "https://search.thesupernaturalbiblechanges.com/changes/2" in joined


def test_format_change_lines_multiple_notes_bulleted():
    change = {
        "ID": 8,
        "BCV": "Genesis 1:3",
        "notes": "first note\nsecond note",
    }

    joined = "\n".join(format_change_lines(change))

    assert "Notes:" in joined
    assert "- first note" in joined
    assert "- second note" in joined


def test_format_change_lines_changed_from_to():
    change = {
        "ID": 7,
        "BCV": "John 1:1",
        "changeType": "Word",
        "notes": "",
        "memorySummary": {
            "restoredText": "",
            "changedFrom": "a god",
            "changedTo": "God",
        },
    }

    joined = "\n".join(format_change_lines(change))

    assert "a god" in joined
    assert "God" in joined


def test_format_change_lines_minimal():
    change = {"ID": 3, "BCV": "Psalm 9:11"}

    lines = format_change_lines(change)

    assert lines == [
        "**Change recorded for Psalm 9:11 (KJV):**",
        "https://search.thesupernaturalbiblechanges.com/changes/3",
    ]