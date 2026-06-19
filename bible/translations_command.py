import discord
from bible.translations_constants import translation_names
async def translations(ctx):
    """Displays available translations"""
    description = ""
    for key in translation_names:
        name = translation_names[key]
        description += f"** {key} ** - {name}\n"

    embeds = []
    for descript in pagify(
        description, page_length=3950, delims=["```", "\n", "\n\n", "**"]
    ):
        verbose_title = "Available Translations"
        embed = discord.Embed(
            title=verbose_title, description=descript, color=discord.Color.green()
        )
        embeds.append(embed)
    await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)
