import os
import json
import re

from bible.translations_constants import translation_names
from bible.book_constants import (
    books_apocrypha,
    books_new_testament,
    books_old_testament,
)

def get_book_extras_from_json(path: str, data, translation: str = 'akjv'):
    book_name = data['book']
    matched_book = match_book(book_name)
    if matched_book is not None:
        book_filename = os.path.join(translation, book_name + '.json')
        # read json, pull out the description
        with open(os.path.join(path, book_filename)) as json_file:
            data = json.load(json_file)
            isString = isinstance(data['book'], str)
            if isString:
                display_extras = get_book_extras(matched_book, translation)
            else:
                display_extras = [
                    data['book']['description']
                ]
                #display_extras = data['book']['meta'][0]['h'] + data['book']['description']

    return display_extras


def get_verse_offset(content):
    offset = 0
    for item in content:
        if 'verseNumber' in item:
            return offset
        offset += 1

    return offset


def detect_translation(message: str):
    translation = None
    parse_translation = re.compile(r'\s(\w+)$')
    if parse_translation.search(message) is not None:
        check_translation = parse_translation.search(message)[1]
        match check_translation.lower():
            case 'asv':
                translation = 'asv'
            case 'bsb':
                translation = 'bsb'
            case 'akjv':
                translation = 'akjv'
            case 'kjv':
                translation = 'akjv'

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
        display_extras = get_book_extras(matched_book, translation)
        return {
            'book': book_name,
            'filename': book_filename,
            'extras': display_extras,
            'matched': matched_book
        }
    return None


def get_book_extras(matched_book: dict, translation: str = 'akjv'):
    extras = []
    if matched_book['order'] <= 66:
        translation_name = translation_names.get(translation)
        extras.append(translation_name)
    if matched_book['order'] > 66:
        extras.append('Apocrypha')
    return extras
