import discord
import os
import json
import re
from redbot.core import commands, Config
from typing import Union
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify, box
from redbot.core.data_manager import bundled_data_path




from .search_command import search
from .search_command import isearch
from .translations_constants import translation_names
from .book_constants import book_categories, books_old_testament, books_new_testament, books_apocrypha

class Bible(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700)
        default_global = {"Notes": []}
        self.config.register_global(**default_global)

    @commands.hybrid_group(name="bible")
    async def bible(self, ctx: commands.Context):
        """Searches for a verse or chapter in the bible"""
        pass

    @bible.command(name="translations")
    async def translations(self, ctx: commands.Context):
        """Displays available translations"""
        await translations(ctx)


        try:
            translation = "akjv"
            detected_translation = False
            # detect if the message ends with a specific translation
            if has_translation(message):
                translation = detect_translation(message)
                detected_translation = True
                # truncate translation from message
                message = message.rsplit(" ", 1)[0]

            res = message.rsplit(" ", 1)
            book = res[0]
            # format and map books to filename
            book_info = get_book_info(book, translation)
            if book_info is None:
                await ctx.send(
                    "Invalid argument: message "
                    + message
                    + " book: "
                    + book
                    + " detected: "
                    + str(detected_translation)
                )
                return

            book_filename = book_info["filename"]
            display_name = book_info["matched"]["name"]
            display_extras = book_info["extras"]

            have_chapter_and_verse = False
            chapter_verse = res[1]
            if ":" in chapter_verse:
                chapter, verse = chapter_verse.split(":")
                chapter = int(chapter)
                have_chapter_and_verse = True
            else:
                chapter = int(chapter_verse)
        except ValueError:
            await ctx.send(
                "Invalid argument: message " + message + " check_path " + check_path
            )
            return

        if have_chapter_and_verse:
            try:
                verse_min, verse_max = verse.split("-")
                verse_min = int(verse_min)
                verse_max = int(verse_max)

            except ValueError:
                try:
                    verse_min = int(verse)
                    verse_max = int(verse)
                except ValueError:
                    await ctx.send("Invalid argument: verse range ", verse)
                    return

        # this is the path to data, the book_filename contains the translation subpath
        path = bundled_data_path(self)

        try:
            with open(os.path.join(path, book_filename)) as json_file:
                data = json.load(json_file)
                embeds = []
                # book_name = get_book_name_from_json(data)
                book_name = book_info["book"]
                # book_info = get_book_info(book)
                display_name = book_info["matched"]["name"]
                display_extras = " ".join(book_info["extras"])

                chapters = data["chapters"]
                chapter = chapters[chapter - 1]
                description = ""

                if not have_chapter_and_verse:
                    # display all verses
                    verse_min = 1
                    verse_max = len(chapter["verses"]) - 1

                # check if the range is valid
                # TODO: extract this into a function
                # try:
                #    if 'verses' in chapter:
                #        chapter.get("verses")[verse_min-1:verse_max]
                # except IndexError:
                #    await ctx.send("Verse not found: ", verse)
                #    return

                # the format between the akjv and the USFM json is different
                usfmFormat = False
                if "verses" in chapter:
                    # non-usfm formatted file
                    verses = chapter.get("verses")[verse_min - 1 : verse_max]
                    chapterNumber = str(chapter["chapter"])
                if "contents" in chapter:
                    usfmFormat = True
                    # find the first index where verseNumber exists,
                    # (each chapter can vary on beginning content)
                    verse_offset = get_verse_offset(chapter.get("contents"))
                    range_min = verse_min + verse_offset - 1
                    range_max = verse_max + verse_offset
                    verses = chapter.get("contents")[range_min:range_max]
                    chapterNumber = chapter.get("chapterNumber")

                for verse in verses:
                    if usfmFormat:
                        # description += "verse json:" + json.dumps(verse) + "\n"
                        verseNumber = verse.get("verseNumber")
                        verseText = verse.get("verseText")
                    else:
                        verseNumber = str(verse["verse"])
                        verseText = verse["text"]
                    description += f"[{verseNumber}] {verseText}\n"
                    if translation == "akjv":
                        async with self.config.Notes() as notes:
                            for note in notes:
                                if note["book"].lower() == book_name:
                                    # Compare with chapter index
                                    if str(note["chapter"]) == chapterNumber:
                                        if str(note["verse"]) == verseNumber:
                                            description += (
                                                str(
                                                    box(
                                                        text="- " + note["note"],
                                                        lang="diff",
                                                    )
                                                )
                                                + "\n"
                                            )

                for descript in pagify(
                    description, page_length=3950, delims=["```", "\n", "\n\n", "**"]
                ):
                    verbose_title = (
                        display_name + " " + chapter_verse + " - " + display_extras
                    )
                    embed = discord.Embed(
                        title=verbose_title,
                        description=descript,
                        color=discord.Color.green(),
                    )
                    embeds.append(embed)

                await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

        except FileNotFoundError:
            await ctx.send("Book not found: ", book_filename)

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

        display_name = book_info["matched"]["name"]

        chapter, verse = chapter_and_verse.split(":")
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
    async def remove(self, ctx: commands.Context, number: int):
        """Removes a note associated with a verse or chapter"""

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
    async def list(
        self,
        ctx: commands.Context,
        book: Union[str, None] = None,
        arg: Union[str, None] = None,
    ):
        """Lists all notes for a verse or chapter"""

        description = ""
        embeds = []
        display_name = None
        if book is not None:
            book_info = get_book_info(book)
            display_name = book_info["matched"]["name"]

        if arg is not None:
            chapter, verse = arg.split(":")
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
                        if (
                            note["book"] == display_name
                            and note["chapter"] == chapter
                            and note["verse"] == verse
                        ):
                            description += f"** {note['number']}: {note['book']} {note['chapter']}:{note['verse']}**\n```diff\n- {note['note']}\n```\n\n"

        if description == "":
            await ctx.send("No notes found")
        else:
            PageNumber = 1
            for descript in pagify(description, page_length=3000, delims=["\n\n"]):
                embed = discord.Embed(
                    title="Notes", description=descript, color=discord.Color.green()
                )
                embed.set_footer(
                    text="Page: {} / {}".format(
                        PageNumber,
                        len(
                            list(pagify(description, page_length=3000, delims=["\n\n"]))
                        ),
                    )
                )
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

    @bible.command(name="search")
    async def search(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case sensitive)"""
        await search(ctx, arg)

    @bible.command(name="isearch")
    async def isearch(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case insensitive)"""
        await search(ctx, arg)

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
            await ctx.send(
                "Incorrect parameters, please try again. Use `{}help` for more information.".format(
                    ctx.prefix
                )
            )
        else:
            # Re-raise the error if it's not an AttributeError or ValueError
            raise error


def get_book_extras_from_json(path: str, data, translation: str = "akjv"):
    book_name = data["book"]
    matched_book = match_book(book_name)
    if matched_book is not None:
        book_filename = os.path.join(translation, book_name + ".json")
        # read json, pull out the description
        with open(os.path.join(path, book_filename)) as json_file:
            data = json.load(json_file)
            isString = isinstance(data["book"], str)
            if isString:
                display_extras = get_book_extras(matched_book, translation)
            else:
                display_extras = [data["book"]["description"]]
                # display_extras = data['book']['meta'][0]['h'] + data['book']['description']

    return display_extras


def get_verse_offset(content):
    offset = 0
    for item in content:
        if "verseNumber" in item:
            return offset
        offset += 1

    return offset


def detect_translation(message: str):
    translation = None
    parse_translation = re.compile(r"\s(\w+)$")
    if parse_translation.search(message) is not None:
        check_translation = parse_translation.search(message)[1]
        match check_translation.lower():
            case "asv":
                translation = "asv"
            case "bsb":
                translation = "bsb"
            case "akjv":
                translation = "akjv"
            case "kjv":
                translation = "akjv"

    return translation


def has_translation(message: str):
    if detect_translation(message) is not None:
        return True
    return False


def match_book(book: str):
    # search OT
    for key in books_old_testament:
        if key == book:
            return books_old_testament[key]
    # search NT
    for key in books_new_testament:
        if key == book:
            return books_new_testament[key]
    # search Apocrypha
    for key in books_apocrypha:
        if key == book:
            return books_apocrypha[key]
    return None


def fix_book_name(book: str):
    book_name = book.strip()
    book_name = book_name.replace(" ", "")
    book_name = book_name.lower()
    match book_name:
        case "psalm":
            book_name = "psalms"
        case "revelations":
            book_name = "revelation"
        case "songsofsolomon":
            book_name = "songofsolomon"
        case "songofsongs":
            book_name = "songofsolomon"
    return book_name


#
# Returns
# - a single lowercase path that will match the case-sensitive file for the specified book
# - a name to be used in display output
# - the Category of the book specified (OT, NT, NC)
# - the name of the translation or collection of books
#


def get_book_info(book: str, translation: str = "akjv"):
    book_name = book.strip()
    book_name = book_name.replace(" ", "")
    book_name = book_name.lower()
    book_name = fix_book_name(book_name)
    matched_book = match_book(book_name)
    if matched_book is not None:
        book_filename = os.path.join(translation, book_name + ".json")
        display_extras = get_book_extras(matched_book, translation)
        return {
            "book": book_name,
            "filename": book_filename,
            "extras": display_extras,
            "matched": matched_book,
        }
    return None


def get_book_extras(matched_book: dict, translation: str = "akjv"):
    extras = []
    if matched_book["order"] <= 66:
        translation_name = translation_names.get(translation)
        extras.append(translation_name)
    if matched_book["order"] > 66:
        extras.append("Apocrypha")
    return extras



# ordered list of books of the bible

books_apocrypha = {
    "enoch": {"name": "Enoch", "order": 67},
}
