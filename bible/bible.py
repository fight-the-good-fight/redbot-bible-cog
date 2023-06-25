import discord
import os
import json
import re
from redbot.core import commands, app_commands, Config
from typing import Union
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify, box
from redbot.core.data_manager import bundled_data_path


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

    @bible.command(name="lookup")
    async def lookup(self, ctx: commands.Context, *, message: str):
        """Displays a chapter for a book, or a specific verse, or a range of verses"""
        try:
            translation = 'akjv'
            # split on last space, this can contain a chapter:verse chapter, or translation
            if has_translation(message):
                translation = detect_translation(message)
                # truncate translation from message
                message = message.rsplit(' ', 1)[0]

            res = message.rsplit(' ', 1)
            book = res[0]
            # format and map books to filename
            book_info = get_book_info(book, translation)
            if book_info is None:
                await ctx.send("Invalid argument: message " + message + " book: " + book)
                return

            book_filename = book_info['filename']
            display_name = book_info['matched']['name']
            display_extras = book_info['extras']

            have_chapter_and_verse = False
            chapter_verse = res[1]
            if (':' in chapter_verse):
                chapter, verse = chapter_verse.split(':')
                chapter = int(chapter)
                have_chapter_and_verse = True
            else:
                chapter = int(chapter_verse)
        except:
            await ctx.send("Invalid argument: message " + message + " book: " + book_filename)
            return

        if have_chapter_and_verse:
            try:
                verse_min, verse_max = verse.split('-')
                verse_min = int(verse_min)
                verse_max = int(verse_max)

            except:
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
                book_name = data["book"]
                book_info = get_book_info(book)
                display_name = book_info['matched']['name']
                display_extras = ' '.join(book_info['extras'])

                chapters = data["chapters"]
                chapter = chapters[chapter-1]
                description = ""

                if not have_chapter_and_verse:
                    # display all verses
                    verse_min = 1
                    verse_max = len(chapter["verses"]) - 1

                try:
                    chapter.get("verses")[verse_min-1:verse_max]
                except IndexError:
                    await ctx.send("Verse not found: ", verse)
                    return

                for verse in chapter.get("verses")[verse_min-1:verse_max]:
                    description += f"[{verse['verse']}] " + \
                        verse['text'] + "\n"
                    async with self.config.Notes() as notes:
                        for note in notes:
                            if note["book"] == book_name:
                                # Compare with chapter index
                                if str(note["chapter"]) == str(chapter["chapter"]):
                                    if str(note["verse"]) == str(verse["verse"]):
                                        description += str(box(text="- " +
                                                        note["note"], lang="diff")) + "\n"

                for descript in pagify(description, page_length=3950, delims=["```", "\n", "\n\n", "**"]):
                    verbose_title = display_name + " " + chapter_verse + " - " + display_extras
                    embed = discord.Embed(
                        title=verbose_title, description=descript, color=discord.Color.green())
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

        # remove leading and ending quotes
        arg = re.sub(r'^"|"$', '', arg)

        translation = 'akjv'
        folder_path = os.path.join(bundled_data_path(self), translation)
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
                    title="Search", description=descript, color=discord.Color.green())
                embed.set_footer(text="Page: {} / {}".format(PageNumber, len(
                    list(pagify(description, page_length=3900, delims=["\n\n"])))))
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

    @bible.command(name="isearch")
    async def isearch(self, ctx: commands.Context, *, arg: str):
        """Searches for matching text across all books (case insensitive)"""

        # remove leading and ending quotes
        arg = re.sub(r'^"|"$', '', arg)

        translation = 'akjv'
        folder_path = os.path.join(bundled_data_path(self), translation)
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
                        matched = re.search(
                            "\\b(" + arg.lower() + ")\\b", verse_text.lower())
                        if matched is not None:
                            description += f"** {book_name} {chapter_num}:{verse_num}**\n{verse_text}\n\n"

        if description == "":
            await ctx.send("No matches found")
        else:
            PageNumber = 1
            for descript in pagify(description, page_length=3950, delims=["\n\n"]):
                embed = discord.Embed(
                    title="Search: Case Insensitive", description=descript, color=discord.Color.green())
                embed.set_footer(text="Page: {} / {}".format(PageNumber, len(
                    list(pagify(description, page_length=3900, delims=["\n\n"])))))
                embeds.append(embed)
                PageNumber += 1

            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=30)

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

def detect_translation(message: str):
    translation = 'akjv'
    parse_translation = re.compile(r'\s(\w+)$')
    if parse_translation.search(message):
        check_translation = parse_translation.match(message).group[1]
        match check_translation.lower():
            case 'bsb':
                translation = 'bsb'
            case 'kjv':
                translation = 'akjv'

    return translation

def has_translation(message: str):
    # split the message, and check the end
    parts = message.split(' ')
    if len(parts) > 1:
        ending = parts[len(parts)-1]
        if detect_translation(ending):
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
    book_name = book_name.replace(' ', '')
    book_name = book_name.lower()
    match book_name:
        case 'psalm':
            book_name = 'psalms'
        case 'revelations':
            book_name = 'revelation'
        case 'songsofsolomon':
            book_name = 'songofsolomon'
        case 'songofsongs':
            book_name = 'songofsolomon'
    return book_name

#
# Returns
# - a single lowercase path that will match the case-sensitive file for the specified book
# - a name to be used in display output
# - the Category of the book specified (OT, NT, NC)
# - the name of the translation or collection of books
#

def get_book_info(book: str, translation: str = 'akjv'):
    book_name = book.strip()
    book_name = book_name.replace(' ', '')
    book_name = book_name.lower()
    book_name = fix_book_name(book_name)
    matched_book = match_book(book_name)
    if matched_book is not None:
        book_filename = os.path.join(translation, book_name + '.json')
        display_extras = get_book_extras(matched_book)
        return {
            'book': book_name,
            'filename': book_filename,
            'extras': display_extras,
            'matched': matched_book
        }
    return None


def get_book_extras(matched_book: dict):
    extras = []
    if matched_book['order'] <= 66:
        extras.append(book_editions[0])
    if matched_book['order'] > 66:
        extras.append(book_editions[1])
    return extras


book_editions = [
    'Authorized (King James) Version (AKJV)',
    'Apocrypha'
]

book_categories = [
    'Old Testament',
    'New Testament',
]
# ordered list of books of the bible
books_old_testament = {
    'genesis': {'name': 'Genesis', 'order': 1},
    'exodus':  {'name': 'Exodus', 'order': 2},
    'leviticus': {'name': 'Leviticus', 'order': 3},
    'numbers': {'name': 'Numbers', 'order': 4},
    'deuteronomy': {'name': 'Deuteronomy', 'order': 5},
    'joshua': {'name': 'Joshua', 'order': 6},
    'judges': {'name': 'Judges', 'order': 7},
    'ruth': {'name': 'Ruth', 'order': 8},
    '1samuel': {'name': '1 Samuel', 'order': 9},
    '2samuel': {'name': '2 Samuel', 'order': 10},
    '1kings': {'name': '1 Kings', 'order': 11},
    '2kings': {'name': '2 Kings', 'order': 12},
    '1chronicles': {'name': '1 Chronicles', 'order': 13},
    '2chronicles': {'name': '2 Chronicles', 'order': 14},
    'ezra': {'name': 'Ezra', 'order': 15},
    'nehemiah': {'name': 'Nehemiah', 'order': 16},
    'esther': {'name': 'Esther', 'order': 17},
    'job': {'name': 'Job', 'order': 18},
    'psalms': {'name': 'Psalms', 'order': 19},
    'proverbs': {'name': 'Proverbs', 'order': 20},
    'ecclesiastes': {'name': 'Ecclesiastes', 'order': 21},
    'songofsolomon': {'name': 'Song of Solomon', 'order': 22},
    'isaiah': {'name': 'Isaiah', 'order': 23},
    'jeremiah': {'name': 'Jeremiah', 'order': 24},
    'lamentations': {'name': 'Lamentations', 'order': 25},
    'ezekiel': {'name': 'Ezekiel', 'order': 26},
    'daniel': {'name': 'Daniel', 'order': 27},
    'hosea': {'name': 'Hosea', 'order': 28},
    'joel': {'name': 'Joel', 'order': 29},
    'amos': {'name': 'Amos', 'order': 30},
    'obadiah': {'name': 'Obadiah', 'order': 31},
    'jonah': {'name': 'Jonah', 'order': 32},
    'micah': {'name': 'Micah', 'order': 33},
    'nahum': {'name': 'Nahum', 'order': 34},
    'habakkuk': {'name': 'Habakkuk', 'order': 35},
    'zephaniah': {'name': 'Zephaniah', 'order': 36},
    'haggai': {'name': 'Haggai', 'order': 37},
    'zechariah': {'name': 'Zechariah', 'order': 38},
    'malachi': {'name': 'Malachi', 'order': 39},
}

books_new_testament = {
    'matthew': {'name': 'Matthew', 'order': 40},
    'mark': {'name': 'Mark', 'order': 41},
    'luke': {'name': 'Luke', 'order': 42},
    'john': {'name': 'John', 'order': 43},
    'acts': {'name': 'Acts', 'order': 44},
    'romans': {'name': 'Romans', 'order': 45},
    '1corinthians': {'name': '1 Corinthians', 'order': 46},
    '2corinthians': {'name': '2 Corinthians', 'order': 47},
    'galatians': {'name': 'Galatians', 'order': 48},
    'ephesians': {'name': 'Ephesians','order':  49},
    'philippians': {'name': 'Philippians', 'order': 50},
    'Colossians': {'name': 'colossians', 'order': 51},
    '1thessalonians': {'name': '1 Thessalonians', 'order': 52},
    '2thessalonians': {'name': '2 Thessalonians','order':  53},
    '1timothy': {'name': '1 Timothy', 'order': 54},
    '2timothy': {'name': '2 Timothy', 'order': 55},
    'titus': {'name': 'titus', 'order': 56},
    'philemon': {'name': 'Philemon', 'order': 57},
    'hebrews': {'name': 'Hebrews', 'order': 58},
    'james': {'name': 'James', 'order': 59},
    '1peter': {'name': '1 Peter', 'order': 60},
    '2peter': {'name': '2 Peter', 'order': 61},
    '1john': {'name': '1 John', 'order': 62},
    '2john': {'name': '2 John', 'order': 63},
    '3john': {'name': '3 John', 'order': 64},
    'jude': {'name': 'Jude', 'order': 65},
    'revelation': {'name': 'Revelation', 'order': 66},
}

books_apocrypha = {
    'enoch': {'name': 'Enoch', 'order': 67},
}
