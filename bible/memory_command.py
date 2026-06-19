import re
import discord
import bible
from typing import Optional, Union
from discord.ext import commands
from discord.ext.commands import Cog
from discord import utils
from bible import Config, get_book_info, pagify


async def add(
    ctx: commands.Context, *, message: str
) -> Optional[discord.Message]:
    """Adds a note to a verse or chapter."""

    parse_add = re.compile(r"^(.*)\s(\d+:\d+)\s(.*)")
    match = parse_add.match(message)
    if not match:
        await ctx.send(
            "Please use the format: **Book** **chapter:verse** Note"
        )
        return None

    book = match.group(1)
    chapter_and_verse = match.group(2)
    note = match.group(3)

    book_info = Bible.get_book_info(book)
    if book_info is None:
        await ctx.send("Book not found: " + book)
        return None

    display_name = book_info["matched"]["name"]

    chapter, verse = chapter_and_verse.split(":")
    chapter = int(chapter)

    try:
        verse = int(verse)
    except ValueError:
        await ctx.send("Verse not found")
        return None

    async with bible.Config.Notes() as notes:
        notes_copy = notes
        for i, note_data in enumerate(notes_copy, start=1):
            note_data["number"] = i
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
    return None


async def remove(ctx: commands.Context, number: int) -> Optional[discord.Message]:
    """Removes a note associated with a verse or chapter."""

    async with bible.Config.Notes() as notes:
        notes_copy = notes

        try:
            notes_copy[number - 1]
        except IndexError:
            await ctx.send("Note not found")
            return None

        for note in notes:
            if note["number"] == number:
                notes.remove(note)
                await ctx.send("Note removed")

        for i, note_data in enumerate(notes_copy, start=1):
            note_data["number"] = i
    return None


async def list_command(
    ctx: commands.Context,
    book: Optional[str] = None,
    arg: Optional[str] = None,
) -> Optional[discord.Message]:
    """Lists all notes for a verse or chapter."""

    description = ""
    display_name = None

    notes = bible.Config.Notes()
    notes_copy = notes

    if book:
        book_info = Bible.get_book_info(book)
        if book_info:
            display_name = book_info["matched"]["name"]

    if arg is not None:
        chapter, verse = arg.split(":")
        chapter = int(chapter) if chapter else None
        verse = int(verse) if verse else None
    else:
        chapter = None
        verse = None

    if display_name is None and arg is None:
        async with bible.Config.Notes() as notes:
            for note in notes:
                description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

    elif display_name is not None and arg is None:
        async with bible.Config.Notes() as notes:
            for note in notes:
                if note["book"] == display_name:
                    description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

    elif display_name is not None and arg is not None:
        if chapter is not None and verse is None:
            async with bible.Config.Notes() as notes:
                for note in notes:
                    if note["book"] == display_name and note["chapter"] == chapter:
                        description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"
        elif chapter is not None and verse is not None:
            async with bible.Config.Notes() as notes:
                for note in notes:
                    if (
                        note["book"] == display_name
                        and note["chapter"] == chapter
                        and note["verse"] == verse
                    ):
                        description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

    if description == "":
        await ctx.send("No notes found.")
        return None

    pages = discord.utils.pagify(description, page_length=3900, delims=["\n\n"])
    page_num = 1
    for page_content in pages:
        embed = discord.Embed(
            title="Notes" + (f" — {display_name}" if display_name else ""),
            description=page_content,
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"Page {page_num}/{len(pages)}")
        await ctx.send(embed=embed)
        page_num += 1
    return None
