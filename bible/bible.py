import json
from pathlib import Path
from typing import Union

from redbot.core import commands

from bible.lookup_command import lookup as lookup_command
from bible.memory_command import add as memory_add_command
from bible.memory_command import list as memory_list_command
from bible.memory_command import remove as memory_remove_command
from bible.memories_store import save_memories
from bible.search_command import isearch as isearch_command
from bible.search_command import search as search_command
from bible.search_utils import get_book_info, has_translation
from bible.translations_command import translations as translations_command

__all__ = ["Bible", "get_book_info", "has_translation"]


class Bible(commands.Cog):
    VERSION = json.loads((Path(__file__).parent / "info.json").read_text())["version"]

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(name="bible")
    async def bible(self, ctx: commands.Context):
        """Searches for a verse or chapter in the bible.

        Use `bible version` to see the cog release.
        """
        pass

    @bible.command(name="version")
    async def version(self, ctx: commands.Context):
        """Shows the Bible cog version"""
        await ctx.send(f"Bible cog version {self.VERSION}")

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
        await memory_add_command(ctx, message=message)

    @memory.command(name="remove")
    @commands.cooldown(1, 1, commands.BucketType.guild)
    async def remove(self, ctx: commands.Context, number: int):
        """Removes a note associated with a verse or chapter"""
        await memory_remove_command(ctx, number)

    @memory.command(name="list")
    async def list(
        self,
        ctx: commands.Context,
        book: Union[str, None] = None,
        arg: Union[str, None] = None,
    ):
        """Lists all notes for a verse or chapter"""
        await memory_list_command(ctx, book=book, arg=arg)

    @bible.command(name="search")
    async def search(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case sensitive)"""
        await search_command(ctx, arg)

    @bible.command(name="isearch")
    async def isearch(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case insensitive)"""
        await isearch_command(ctx, arg)

    @commands.command()
    async def removeallnotes(self, ctx: commands.Context) -> None:
        """Clears all notes"""
        if not await self.bot.is_owner(ctx.author):
            await ctx.send("Only the bot owner can use this command.")
            return
        save_memories([])
        await ctx.send("All notes removed")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if ctx.command is None or ctx.command.cog is not self:
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Missing required argument: `{error.param.name}`. "
                f"Use `{ctx.prefix}help {ctx.command}` for usage."
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f"Bad argument: `{error.args[0] if error.args else 'unknown'}`. "
                f"Use `{ctx.prefix}help {ctx.command}` for usage."
            )
            return

        raise error
