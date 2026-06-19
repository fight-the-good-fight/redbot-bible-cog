import discord
import os
import json
import re
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify, box



async def search(ctx, arg: str):
    """Searches for matching text across all books (case sensitive)"""

    # remove leading and ending quotes
    arg = re.sub(r'^"|"$', "", arg)

    translation = "akjv"
    folder_path = os.path.join(bundled_data_path(ctx.cog), translation)
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
                    matched = re.search("\\b(" + arg + ")\\b", verse_text)
                    if matched is not None:
                        description += f"** {book_name} {chapter_num}:{verse_num}**\n{verse_text}\n\n"

    if description == "":
        await ctx.send("No matches found")
    else:
        PageNumber = 1
        for descript in pagify(description, page_length=3950, delims=["\n\n"]):
            embed = discord.Embed(
                title="Search", description=descript, color=discord.Color.green()
            )
            embed.set_footer(
                text="Page: {} / {}".format(
                    PageNumber,
                    len(
                        list(pagify(description, page_length=3900, delims=["\n\n"]))
                    ),
                )
            )
            embeds.append(embed)
            PageNumber += 1

        await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

