import re
from typing import Union

import discord
from builtins import list as builtin_list
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from bible.search_utils import get_book_info


def _renumber_notes(notes):
    for i, note_data in enumerate(notes, start=1):
        note_data["number"] = i


async def add(cog, ctx, *, message: str) -> None:
    """Adds a note to a verse or chapter"""

    parse_add = re.compile(r"^(.*)\s(\d+:\d+)\s(.*)")
    parsed = parse_add.match(message)
    if parsed is None:
        await ctx.send("Invalid argument: " + message)
        return

    book = parsed.group(1)
    chapter_and_verse = parsed.group(2)
    note = parsed.group(3)
    book_info = get_book_info(book)
    if book_info is None:
        await ctx.send("Book not found: " + book)
        return

    display_name = book_info["matched"]["name"]

    chapter, verse = chapter_and_verse.split(":")
    chapter = int(chapter)

    try:
        verse = int(verse)
    except ValueError:
        await ctx.send("Verse not found")
        return

    async with cog.config.Notes() as notes:
        _renumber_notes(notes)
        notes.append(
            {
                "number": len(notes) + 1,
                "book": display_name,
                "chapter": chapter,
                "verse": verse,
                "note": note,
            }
        )
    await ctx.send(
        "Note added for " + display_name + " " + str(chapter) + ":" + str(verse)
    )


async def remove(cog, ctx, number: int) -> None:
    """Removes a note associated with a verse or chapter"""

    async with cog.config.Notes() as notes:
        notes_copy = notes

        try:
            notes_copy[number - 1]
        except IndexError:
            await ctx.send("Note not found")
            return

        for note in notes:
            if note["number"] == number:
                notes.remove(note)
                await ctx.send("Note removed")
                break

        _renumber_notes(notes_copy)


async def list(
    cog, ctx, book: Union[str, None] = None, arg: Union[str, None] = None
) -> None:
    """Lists all notes for a verse or chapter"""

    description = ""
    embeds = []
    display_name = None

    if book is not None:
        book_info = get_book_info(book)
        if book_info is None:
            await ctx.send("Book not found: " + book)
            return
        display_name = book_info["matched"]["name"]

    if arg is not None:
        chapter, verse = arg.split(":")
        chapter = int(chapter) if chapter else None
        verse = int(verse) if verse else None
    else:
        chapter = None
        verse = None

    if display_name is None and arg is None:
        async with cog.config.Notes() as notes:
            for note in notes:
                description += (
                    f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n"
                    f"```diff\n- {note['note']}\n```\n\n"
                )
    else:
        async with cog.config.Notes() as notes:
            for note in notes:
                if display_name is not None and note["book"] != display_name:
                    continue
                if chapter is not None and note["chapter"] != chapter:
                    continue
                if verse is not None and note["verse"] != verse:
                    continue
                description += (
                    f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n"
                    f"```diff\n- {note['note']}\n```\n\n"
                )

    if description == "":
        await ctx.send("No notes found")
    else:
        PageNumber = 1
        for descript in pagify(description, page_length=3950, delims=["\n\n"]):
            embed = discord.Embed(
                title="Memory", description=descript, color=discord.Color.green()
            )
            embed.set_footer(
                text="Page: {} / {}".format(
                    PageNumber,
                    len(
                        builtin_list(
                            pagify(description, page_length=3900, delims=["\n\n"])
                        )
                    ),
                )
            )
            embeds.append(embed)
            PageNumber += 1

        await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)
