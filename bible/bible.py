from typing import Union

import discord
import json
import os
import re

from redbot.core import Config, app_commands, commands
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from bible.translations_command import translations as translations_command
from bible.search_command import isearch as isearch_command
from bible.search_command import search as search_command
from bible.lookup_command import lookup as lookup_command
from bible.search_utils import has_translation, detect_translation, get_book_info, get_verse_offset

class Bible(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700)
        default_global = {
            "Notes": []
        }
        self.config.register_global(**default_global)

    @commands.hybrid_group(name="bible")
    async def bible(self, ctx: commands.Context):
        """Searches for a verse or chapter in the bible"""
        pass

    @bible.command(name="translations")
    async def translations(self, ctx: commands.Context):
        """Displays available translations"""
        await translations_command(ctx)

    @bible.command(name="lookup")
    async def lookup(self, ctx: commands.Context, *, message: str):
        """Displays a chapter for a book, or a specific verse, or a range of verses"""
        await lookup_command(self, ctx, message)

    @commands.hybrid_group(name="memory")
    async def memory(self, ctx: commands.Context):
        """Manage for each verse or chapter of the bible"""
        pass

    @memory.command(name="add")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    async def add(self, ctx: commands.Context, *, message: str):
        """Adds a note to a verse or chapter"""

        parse_add = re.compile(r"^(.*)\s(\d+:\d+)\s(.*)")
        book = parse_add.match(message).group(1)
        chapter_and_verse = parse_add.match(message).group(2)
        note = parse_add.match(message).group(3)
        book_info = get_book_info(book)
        if book_info is None:
            await ctx.send("Book not found: " + book)
            return

        display_name = book_info['matched']['name']

        chapter, verse = chapter_and_verse.split(':')
        chapter = int(chapter)

        try:
            verse = int(verse)

        except ValueError:
            await ctx.send("Verse not found")

        async with self.config.Notes() as notes:
            notes_copy = notes
            for i, note_data in enumerate(notes_copy, start=1):
                note_data["number"] = i
                # notes.append(note)
            notes.append({"number": len(notes)+1, "book": display_name,
                        "chapter": chapter, "verse": verse, "note": note})
        await ctx.send("Note added for " + display_name + " " + str(chapter) + ":" + str(verse))

    @memory.command(name="remove")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    async def remove(self, ctx: commands.Context, number: int):
        """Removes a note associated with a verse or chapter"""

        async with self.config.Notes() as notes:
            notes_copy = notes

            try:
                notes_copy[number-1]
            except IndexError:
                await ctx.send("Note not found")
                return

            for note in notes:
                if note["number"] == number:
                    notes.remove(note)
                    await ctx.send("Note removed")

            for i, note_data in enumerate(notes_copy, start=1):
                note_data["number"] = i

    @memory.command(name="list")
    async def list(self, ctx: commands.Context, book: Union[str, None] = None, arg: Union[str, None] = None):
        """Lists all notes for a verse or chapter"""

        description = ""
        embeds = []
        display_name = None
        if book is not None:
            book_info = get_book_info(book)
            display_name = book_info['matched']['name']

        if arg is not None:
            chapter, verse = arg.split(':')
            chapter = int(chapter) if chapter else None
            verse = int(verse) if verse else None
        else:
            chapter = None
            verse = None

        if display_name is None and arg is None:
            async with self.config.Notes() as notes:
                for note in notes:
                    description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

        elif display_name is not None and arg is None:
            async with self.config.Notes() as notes:
                for note in notes:
                    if note["book"] == display_name:
                        description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

        elif display_name is not None and arg is not None:
            if chapter is not None and verse is None:
                async with self.config.Notes() as notes:
                    for note in notes:
                        if note["book"] == display_name and note["chapter"] == chapter:
                            description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"
            elif chapter is not None and verse is not None:
                async with self.config.Notes() as notes:
                    for note in notes:
                        if note["book"] == display_name and note["chapter"] == chapter and note["verse"] == verse:
                            description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

        if description == "":
            await ctx.send("No notes found")
        else:
            PageNumber = 1
            for descript in pagify(description, page_length=3000, delims=["\n\n"]):
                embed = discord.Embed(
                    title="Notes", description=descript, color=discord.Color.green())
                embed.set_footer(text="Page: {} / {}".format(PageNumber, len(
                    list(pagify(description, page_length=3000, delims=["\n\n"])))))
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

    @bible.command(name="search")
    async def search(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case sensitive)"""
        await search_command(ctx, arg)

    @bible.command(name="isearch")
    async def isearch(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case insensitive)"""
        await isearch_command(ctx, arg)

    @commands.command()
    @commands.is_owner()
    async def removeallnotes(self, ctx: commands.Context):
        """Clears all notes"""
        await self.config.clear_all()
        await ctx.send("All Notes removed")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore CommandNotFound errors

        if isinstance(error, (AttributeError, ValueError)):
            await ctx.send("Incorrect parameters, please try again. Use `{}help` for more information.".format(ctx.prefix))
        else:
            # Re-raise the error if it's not an AttributeError or ValueError
            raise error
