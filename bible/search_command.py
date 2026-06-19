import discord
import re
import os
import json
from typing import List
from discord.ext import commands
from redbot.core.data_manager import bundled_data_path
from redbot.core.i18n import Translator
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify

_ = Translator("Bible", __file__)

from bible.bible import Bible


class SearchCommand(commands.Cog):
    """Search command: search across all books (case-sensitive)."""

    @commands.command(name="search")
    @commands.guild_only()
    async def search_command(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case sensitive)."""
        # remove leading and ending quotes
        arg = re.sub(r'^"|"$', "", arg)

        translation = "akjv"
        folder_path = os.path.join(bundled_data_path(ctx.bot), translation)
        description = ""
        embeds = []

        for filename in os.listdir(folder_path):
            with open(os.path.join(folder_path, filename), "r") as file:
                data = json.load(file)
                book_name = data["book"]
                chapters = data["chapters"]
                for chapter in chapters:
                    chapter_num = chapter["chapter"]
                    verses = chapter["verses"]
                    for verse in verses:
                        verse_num = verse["verse"]
                        verse_text = verse["text"]
                        matched = re.search(r"\b(" + arg + r")\b", verse_text)
                        if matched is not None:
                            description += f"** {book_name} {chapter_num}:{verse_num}**\n{verse_text}\n\n"

        if description == "":
            await ctx.send(_("No matches found"))
        else:
            PageNumber = 1
            for descript in pagify(description, page_length=3950, delims=["\n\n"]):
                embed = discord.Embed(
                    title="Search", description=descript, color=discord.Color.green()
                )
                embed.set_footer(
                    text="Page: {} / {}".format(
                        PageNumber,
                        len(list(pagify(description, page_length=3900, delims=["\n\n"]))),
                    )
                )
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

    @commands.command(name="isearch")
    @commands.guild_only()
    async def isearch_command(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case insensitive)."""
        # remove leading and ending quotes
        arg = re.sub(r'^"|"$', "", arg)

        translation = "akjv"
        folder_path = os.path.join(bundled_data_path(ctx.bot), translation)
        description = ""
        embeds = []

        for filename in os.listdir(folder_path):
            with open(os.path.join(folder_path, filename), "r") as file:
                data = json.load(file)
                book_name = data["book"]
                chapters = data["chapters"]
                for chapter in chapters:
                    chapter_num = chapter["chapter"]
                    verses = chapter["verses"]
                    for verse in verses:
                        verse_num = verse["verse"]
                        verse_text = verse["text"]
                        matched = re.search(r"\b(" + arg.lower() + r")\b", verse_text.lower())
                        if matched is not None:
                            description += f"** {book_name} {chapter_num}:{verse_num}**\n{verse_text}\n\n"

        if description == "":
            await ctx.send(_("No matches found"))
        else:
            PageNumber = 1
            for descript in pagify(description, page_length=3950, delims=["\n\n"]):
                embed = discord.Embed(
                    title="Search: Case Insensitive",
                    description=descript,
                    color=discord.Color.green(),
                )
                embed.set_footer(
                    text="Page: {} / {}".format(
                        PageNumber,
                        len(list(pagify(description, page_length=3900, delims=["\n\n"]))),
                    )
                )
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

    async def cog_load(self):
        """Register the search command."""
        self.bot = ctx.bot  # type: ignore


def setup(bot: commands.Bot):
    """Setup function for the search command."""
    bot.add_cog(SearchCommand(bot))
