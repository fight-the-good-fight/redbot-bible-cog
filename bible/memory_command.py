import re
from typing import Optional, Union
from discord.ext import commands
from redbot.core.i18n import Translator
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify
from discord.embeds import Embed

_ = Translator("Bible", __file__)

from bible.bible import Bible


class MemoryCommand(commands.Cog):
    """Memory command: manage notes for verses."""

    @commands.hybrid_group(name="memory")
    @commands.guild_only()
    async def memory(self, ctx: commands.Context):
        """Manage for each verse or chapter of the bible."""
        pass

    @memory.command(name="add")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    @commands.guild_only()
    async def add(self, ctx: commands.Context, *, message: str):
        """Adds a note to a verse or chapter."""

        parse_add = re.compile(r"^(.*)\s(\d+:\d+)\s(.*)")
        match = parse_add.match(message)
        if not match:
            await ctx.send(
                _("Please use the format: **Book** **chapter:verse** Note")
            )
            return

        book = match.group(1)
        chapter_and_verse = match.group(2)
        note = match.group(3)

        book_info = Bible.get_book_info(book)
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

        async with self.config.Notes() as notes:
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

    @memory.command(name="remove")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, number: int):
        """Removes a note associated with a verse or chapter."""

        async with self.config.Notes() as notes:
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

            for i, note_data in enumerate(notes_copy, start=1):
                note_data["number"] = i

    @memory.command(name="list")
    @commands.guild_only()
    async def list_command(
        self,
        ctx: commands.Context,
        book: Union[str, None] = None,
        arg: Union[str, None] = None,
    ):
        """Lists all notes for a verse or chapter."""

        description = ""
        embeds = []
        display_name = None

        notes = self.config.Notes()
        notes_copy = notes

        if book:
            book_info = Bible.get_book_info(book)
            if book_info:
                display_name = book_info["matched"]["name"]

        notes_copy = notes
        for i, note_data in enumerate(notes_copy, start=1):
            if book:
                if note_data["book"] != display_name:
                    continue
            description += f"**Note {note_data['number']}:** {note_data['note']}\n\n"

        if description == "":
            await ctx.send(_("No notes found."))
            return

        pages = pagify(description, page_length=3900, delims=["\n\n"])
        page_num = 1
        for page_content in pages:
            embed = Embed(
                title="Notes" + (f" — {display_name}" if display_name else ""),
                description=page_content,
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Page {page_num}/{len(pages)}")
            await ctx.send(embed=embed)
            page_num += 1

    async def cog_load(self):
        """Register the memory command."""
        self.bot = ctx.bot  # type: ignore


def setup(bot: commands.Bot):
    """Setup function for the memory command."""
    bot.add_cog(MemoryCommand(bot))
