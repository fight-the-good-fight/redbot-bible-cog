"""Tests for search_command.py."""

import asyncio
import re
from pathlib import Path
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
def akjv_data_dir():
    return Path(__file__).resolve().parents[1] / "data" / "akjv"


@pytest.fixture
def mock_bundled_data_path():
    return Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def mock_search_result():
    return """** Genesis 1:1 **
In the beginning God created the heavens and the earth.

** Genesis 1:2 **
Now the earth was formless and void, and darkness was over the surface of the deep."""


async def test_search_basic(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, "test")

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", "test")
                            mock_re_search.assert_called()
                            assert mock_pagify.call_count >= 1
                            mock_embed.assert_called_once()
                            assert mock_embed.call_args[1]["title"] == "Search"
                            mock_menu.assert_awaited_once()


async def test_search_quotes(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, '"test"')

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", '"test"')
                            mock_embed.assert_called_once()
                            assert mock_embed.call_args[1]["title"] == "Search"
                            assert mock_pagify.call_count >= 1
                            mock_menu.assert_awaited_once()


async def test_search_no_matches(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="no match") as mock_re_sub:
                with patch("bible.search_command.re.search", return_value=None) as mock_re_search:
                    with patch("bible.search_command.pagify") as mock_pagify:
                        await search(mock_ctx, "no match")

                    mock_re_sub.assert_called_once_with(r'^"|"$', "", "no match")
                    mock_re_search.assert_called()
                    mock_pagify.assert_not_called()
                    mock_ctx.send.assert_awaited_once_with("No matches found")


async def test_search_translation_specifier(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, "kjv genesis 1:1")

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", "kjv genesis 1:1")
                            mock_embed.assert_called_once()
                            assert mock_embed.call_args[1]["title"] == "Search"
                            mock_menu.assert_awaited_once()


async def test_search_translation_specifier_invalid(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, "invalid genesis 1:1")

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", "invalid genesis 1:1")
                            mock_embed.assert_called_once()
                            assert mock_embed.call_args[1]["title"] == "Search"
                            mock_menu.assert_awaited_once()


async def test_search_quotes(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await search(mock_ctx, '"test"')

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", '"test"')
                            mock_embed.assert_called_once()
                            assert mock_embed.call_args[1]["title"] == "Search"
                            mock_menu.assert_awaited_once()


async def test_isearch_basic(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await isearch(mock_ctx, "test")

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", "test")
                            mock_re_search.assert_called()
                            assert mock_pagify.call_count >= 1
                            assert mock_embed.call_args[1]["title"] == "Case-Insensitive Search"
                            mock_menu.assert_awaited_once()


async def test_isearch_translation_specifier(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="test") as mock_re_sub:
                with patch("bible.search_command.re.search") as mock_re_search:
                    mock_match = MagicMock()
                    mock_match.group.return_value = "test"
                    mock_re_search.return_value = mock_match

                    with patch("bible.search_command.pagify", return_value=["page1"]) as mock_pagify:
                        with patch("bible.search_command.discord.Embed") as mock_embed:
                            with patch("bible.search_command.menu", new=AsyncMock()) as mock_menu:
                                await isearch(mock_ctx, "kjv genesis 1:1")

                            mock_re_sub.assert_called_once_with(r'^"|"$', "", "kjv genesis 1:1")
                            assert mock_embed.call_args[1]["title"] == "Case-Insensitive Search"
                            mock_menu.assert_awaited_once()


async def test_isearch_quotes(mock_ctx, akjv_data_dir, mock_bundled_data_path):
    with patch("bible.search_command.bundled_data_path", return_value=str(mock_bundled_data_path)):
        with patch("bible.search_command.Path") as mock_path:
            mock_path.return_value.joinpath.return_value = akjv_data_dir
            with patch("bible.search_command.re.sub", return_value="no match") as mock_re_sub:
                with patch("bible.search_command.re.search", return_value=None) as mock_re_search:
                    with patch("bible.search_command.pagify") as mock_pagify:
                        await isearch(mock_ctx, '"no match"')

                    mock_re_sub.assert_called_once_with(r'^"|"$', "", '"no match"')
                    mock_re_search.assert_called()
                    mock_pagify.assert_not_called()
                    mock_ctx.send.assert_awaited_once_with("No matches found")
