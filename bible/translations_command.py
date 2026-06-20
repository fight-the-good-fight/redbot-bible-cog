import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from bible.translations_constants import translation_names


async def translations(ctx: commands.Context):
    """Displays available translations"""
    description = ""
    for key in translation_names:
        name = translation_names[key]
        description += f"** {key} ** - {name}\n"

    embeds = []
    for descript in pagify(description, page_length=3950, delims=["```", "\n", "\n\n", "**"]):
        verbose_title = "Available Translations"
        embed = discord.Embed(
            title=verbose_title, description=descript, color=discord.Color.green()
        )
        embeds.append(embed)

    await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)
