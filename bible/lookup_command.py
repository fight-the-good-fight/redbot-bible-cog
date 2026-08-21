import json
import os

import discord
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from bible.changes_api import get_changes_for_chapter
from bible.memories_store import load_memories
from bible.verse_blocks import render_chapter_lines
from bible.search_utils import (
    detect_translation,
    get_book_info,
    has_translation,
)


async def lookup(cog, ctx, message: str):
    """Displays a chapter for a book, or a specific verse, or a range of verses"""
    check_path = bundled_data_path(cog)

    try:
        translation = "akjv"
        if has_translation(message):
            detected = detect_translation(message)
            if detected is not None:
                translation = detected
            message = message.rsplit(" ", 1)[0]

        res = message.rsplit(" ", 1)
        book = res[0]
        book_info = get_book_info(book, translation)
        if book_info is None:
            return

        book_filename = book_info["filename"]
        display_name = book_info["matched"]["name"]
        display_extras = book_info["extras"]

        have_chapter_and_verse = False
        chapter_verse = res[1]
        if ":" in chapter_verse:
            chapter, verse = chapter_verse.split(":")
            chapter = int(chapter)
            if verse:
                have_chapter_and_verse = True
        else:
            chapter = int(chapter_verse)
    except Exception:
        await ctx.send(
            "Invalid argument: message " + message + " check_path " + str(check_path)
        )
        return

    verse_list = []
    if have_chapter_and_verse:
        try:
            for item in verse.split(","):
                if "-" in item:
                    a, b = item.split("-")
                    verse_list.extend(range(int(a), int(b) + 1))
                else:
                    verse_list.append(int(item))
        except (ValueError, AttributeError):
            await ctx.send("Invalid argument: verse range " + verse)
            return
        verse_list = list(dict.fromkeys(verse_list))

    path = bundled_data_path(cog)

    try:
        with open(os.path.join(path, book_filename)) as json_file:
            data = json.load(json_file)
            embeds = []
            book_name = book_info["book"]
            display_name = book_info["matched"]["name"]
            display_extras = " ".join(book_info["extras"])

            chapters = data["chapters"]
            if chapter < 1 or chapter > len(chapters):
                await ctx.send("Invalid chapter or verse")
                return
            chapter = chapters[chapter - 1]

            usfmFormat = False
            if "verses" in chapter:
                all_verses = chapter["verses"]
                chapterNumber = str(chapter["chapter"])
                by_number = {int(v["verse"]): v for v in all_verses}
                if have_chapter_and_verse:
                    if any(n not in by_number for n in verse_list):
                        await ctx.send("Invalid chapter or verse")
                        return
                    verses = [by_number[n] for n in verse_list]
                else:
                    verses = all_verses
            if "contents" in chapter:
                usfmFormat = True
                contents = chapter["contents"]
                chapterNumber = chapter.get("chapterNumber")
                by_number = {
                    int(c["verseNumber"]): c
                    for c in contents
                    if isinstance(c, dict) and "verseNumber" in c
                }
                if have_chapter_and_verse:
                    if any(n not in by_number for n in verse_list):
                        await ctx.send("Invalid chapter or verse")
                        return
                    verses = [by_number[n] for n in verse_list]
                else:
                    verses = [
                        c
                        for c in contents
                        if isinstance(c, dict) and "verseNumber" in c
                    ]

            # Build description and collect notes once per chapter.
            notes_by_verse: dict[str, list[str]] = {}
            if translation == "akjv":
                notes = load_memories()
                if usfmFormat:
                    verse_numbers = {
                        str(verse.get("verseNumber")) for verse in verses if "verseNumber" in verse
                    }
                else:
                    verse_numbers = {str(verse["verse"]) for verse in verses}

                chapter_notes = [
                    note
                    for note in notes
                    if note["book"].lower() == book_name
                    and str(note["chapter"]) == chapterNumber
                    and str(note["verse"]) in verse_numbers
                ]
                for note in chapter_notes:
                    verse_key = str(note["verse"])
                    notes_by_verse.setdefault(verse_key, []).append(
                        str(note["note"])
                    )

            changes_by_verse: dict[str, list[dict]] = {}
            if translation == "akjv" and have_chapter_and_verse:
                book_number = book_info["matched"]["order"]
                if book_number <= 66 and chapterNumber is not None:
                    changes = await get_changes_for_chapter(
                        book_number, int(chapterNumber)
                    )
                    for change in changes:
                        verse_key = str(change.get("verse"))
                        if verse_key not in verse_numbers:
                            continue
                        changes_by_verse.setdefault(verse_key, []).append(change)

            render_ctx = {
                "notes_by_verse": notes_by_verse,
                "changes_by_verse": changes_by_verse,
            }
            description = "\n".join(render_chapter_lines(verses, render_ctx))

            for descript in pagify(
                description, page_length=3950, delims=["```", "\n\n"]
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
        await ctx.send("Book not found: " + book_filename)
