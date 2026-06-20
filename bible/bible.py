from typing import Union

import discord

from redbot.core import Config, app_commands, commands

from bible.lookup_command import lookup as lookup_command
from bible.memory_command import add as memory_add_command
from bible.memory_command import list as memory_list_command
from bible.memory_command import remove as memory_remove_command
from bible.search_command import isearch as isearch_command
from bible.search_command import search as search_command
from bible.search_utils import detect_translation, get_book_info, get_verse_offset, has_translation
from bible.translations_command import translations as translations_command

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
        await memory_add_command(self, ctx, message=message)

    @memory.command(name="remove")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    async def remove(self, ctx: commands.Context, number: int):
        """Removes a note associated with a verse or chapter"""
        await memory_remove_command(self, ctx, number)

    @memory.command(name="list")
    async def list(self, ctx: commands.Context, book: Union[str, None] = None, arg: Union[str, None] = None):
        """Lists all notes for a verse or chapter"""
        await memory_list_command(self, ctx, book=book, arg=arg)

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
