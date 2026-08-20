import json
import os

import discord
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from bible.changes_api import get_changes_for_chapter
from bible.memories_store import load_memories
from bible.verse_blocks import render_verse_lines
from bible.search_utils import (
    detect_translation,
    get_book_info,
    get_verse_offset,
    has_translation,
)


async def lookup(cog, ctx, message: str):
    """Displays a chapter for a book, or a specific verse, or a range of verses"""
    check_path = bundled_data_path(cog)

    try:
        translation = "akjv"
        detected_translation = False
        if has_translation(message):
            detected_translation = True
            detected = detect_translation(message)
            if detected is not None:
                translation = detected
            message = message.rsplit(" ", 1)[0]

        res = message.rsplit(" ", 1)
        book = res[0]
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
    except Exception:
        await ctx.send(
            "Invalid argument: message " + message + " check_path " + str(check_path)
        )
        return

    if have_chapter_and_verse:
        try:
            verse_min, verse_max = verse.split("-")
            verse_min = int(verse_min)
            verse_max = int(verse_max)
        except Exception:
            try:
                verse_min = int(verse)
                verse_max = int(verse)
            except ValueError:
                await ctx.send("Invalid argument: verse range " + verse)
                return

    path = bundled_data_path(cog)

    try:
        with open(os.path.join(path, book_filename)) as json_file:
            data = json.load(json_file)
            embeds = []
            book_name = book_info["book"]
            display_name = book_info["matched"]["name"]
            display_extras = " ".join(book_info["extras"])

            chapters = data["chapters"]
            chapter = chapters[chapter - 1]
            description_lines = []

            if not have_chapter_and_verse:
                verse_min = 1
                verse_max = len(chapter["verses"]) - 1

            usfmFormat = False
            if "verses" in chapter:
                verses = chapter.get("verses")[verse_min - 1 : verse_max]
                chapterNumber = str(chapter["chapter"])
            if "contents" in chapter:
                usfmFormat = True
                verse_offset = get_verse_offset(chapter.get("contents"))
                range_min = verse_min + verse_offset - 1
                range_max = verse_max + verse_offset
                verses = chapter.get("contents")[range_min:range_max]
                chapterNumber = chapter.get("chapterNumber")

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

            ctx = {
                "notes_by_verse": notes_by_verse,
                "changes_by_verse": changes_by_verse,
            }
            for verse in verses:
                description_lines.extend(render_verse_lines(verse, ctx))

            description = "\n".join(description_lines)

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
