import re
from pathlib import Path

import discord
from bible.search_index import search_verses_sqlite
from bible.search_utils import detect_translation
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu


def _search_index_path(ctx) -> str:
    return str(Path(bundled_data_path(ctx.cog)).joinpath("search_index.sqlite"))


def _render_rows(title: str, rows: list[dict[str, object]]):
    description = "\n\n".join(
        f"** {row['book']} {row['chapter']}:{row['verse']}**\n{row['text']}" for row in rows
    )
    embeds = []
    pages = list(pagify(description, page_length=3900, delims=["\n\n"]))
    for page_number, descript in enumerate(
        pagify(description, page_length=3950, delims=["\n\n"]), start=1
    ):
        embed = discord.Embed(title=title, description=descript, color=discord.Color.green())
        embed.set_footer(text=f"Page: {page_number} / {len(pages)}")
        embeds.append(embed)
    return embeds


async def search(ctx, arg: str):
    """Searches for matching text across all books (case sensitive)"""

    arg = re.sub(r'^"|"$', "", arg)
    translation = detect_translation(arg) or "akjv"
    rows = search_verses_sqlite(_search_index_path(ctx), arg, case_insensitive=False, translation=translation)
    if not rows:
        await ctx.send("No matches found")
        return

    await menu(ctx, _render_rows("Search", rows), controls=DEFAULT_CONTROLS, timeout=30)


async def isearch(ctx, arg: str):
    """Searches for matching text across all books (case insensitive)"""

    arg = re.sub(r'^"|"$', "", arg)
    translation = detect_translation(arg) or "akjv"
    rows = search_verses_sqlite(_search_index_path(ctx), arg, case_insensitive=True, translation=translation)
    if not rows:
        await ctx.send("No matches found")
        return

    await menu(ctx, _render_rows("Case-Insensitive Search", rows), controls=DEFAULT_CONTROLS, timeout=30)
