from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bible.search_command import isearch, search


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.cog = MagicMock()
    return ctx


@pytest.fixture
def mock_index_path():
    return "search.sqlite"


@pytest.fixture
def mock_rows():
    return [
        {
            "book": "Genesis",
            "chapter": 1,
            "verse": 1,
            "text": "In the beginning God created the heavens and the earth.",
        },
        {
            "book": "Genesis",
            "chapter": 1,
            "verse": 2,
            "text": "And the earth was without form, and void.",
        },
    ]


async def test_search_basic(mock_ctx, mock_index_path, mock_rows):
    with patch("bible.search_command.re.sub", return_value="test") as mock_sub:
        with patch("bible.search_command.detect_translation", return_value=None) as mock_detect:
            with patch("bible.search_command._search_index_path", return_value=mock_index_path):
                with patch("bible.search_command.search_verses_sqlite", return_value=mock_rows) as mock_search:
                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, '"test"')

    mock_sub.assert_called_once_with(r'^"|"$', "", '"test"')
    mock_detect.assert_called_once_with("test")
    mock_search.assert_called_once_with(
        mock_index_path, "test", case_insensitive=False, translation="akjv"
    )
    assert mock_pagify.call_count == 2
    mock_embed.assert_called_once()
    assert mock_embed.call_args.kwargs["title"] == "Search"
    mock_menu.assert_awaited_once()


async def test_search_no_matches(mock_ctx):
    with patch("bible.search_command.re.sub", return_value="test"):
        with patch("bible.search_command.detect_translation", return_value=None):
            with patch("bible.search_command._search_index_path", return_value="search.sqlite"):
                with patch("bible.search_command.search_verses_sqlite", return_value=[]):
                    with patch("bible.search_command.pagify") as mock_pagify:
                        await search(mock_ctx, "test")

    mock_pagify.assert_not_called()
    mock_ctx.send.assert_awaited_once_with("No matches found")


async def test_isearch_basic(mock_ctx, mock_index_path, mock_rows):
    with patch("bible.search_command.re.sub", return_value="test"):
        with patch("bible.search_command.detect_translation", return_value="bsb"):
            with patch("bible.search_command._search_index_path", return_value=mock_index_path):
                with patch("bible.search_command.search_verses_sqlite", return_value=mock_rows) as mock_search:
                    with patch("bible.search_command.pagify", return_value=["page1"]):
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await isearch(mock_ctx, "test")

    mock_search.assert_called_once_with(
        mock_index_path, "test", case_insensitive=True, translation="bsb"
    )
    assert mock_embed.call_args.kwargs["title"] == "Case-Insensitive Search"
    mock_menu.assert_awaited_once()


async def test_isearch_no_matches(mock_ctx):
    with patch("bible.search_command.re.sub", return_value="test"):
        with patch("bible.search_command.detect_translation", return_value=None):
            with patch("bible.search_command._search_index_path", return_value="search.sqlite"):
                with patch("bible.search_command.search_verses_sqlite", return_value=[]):
                    with patch("bible.search_command.pagify") as mock_pagify:
                        await isearch(mock_ctx, "test")

    mock_pagify.assert_not_called()
    mock_ctx.send.assert_awaited_once_with("No matches found")
