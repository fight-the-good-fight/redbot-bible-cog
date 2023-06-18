import sys
sys.path.append('../')

from bible import get_book_info

def test_get_book_info():
    book_info = get_book_info('Genesis')
    assert book_info['book'] == 'genesis'
    assert book_info['filename'] == 'genesis.json'
    assert book_info['matched']['name'] == 'Genesis'
    assert book_info['matched']['order'] == 1
    assert book_info['extras'] == ['Authorized (King James) Version (AKJV)']

    book_info = get_book_info('genesis')
    assert book_info['book'] == 'genesis'
    assert book_info['filename'] == 'genesis.json'
    assert book_info['matched']['name'] == 'Genesis'
    assert book_info['matched']['order'] == 1
    assert book_info['extras'] == ['Authorized (King James) Version (AKJV)']

    book_info = get_book_info('Song of Solomon')
    assert book_info['book'] == 'songofsolomon'
    assert book_info['filename'] == 'songofsolomon.json'
    assert book_info['matched']['name'] == 'Song of Solomon'
    assert book_info['matched']['order'] == 22
    assert book_info['extras'] == ['Authorized (King James) Version (AKJV)']

    book_info = get_book_info('Song of Songs')
    assert book_info['book'] == 'songofsolomon'
    assert book_info['filename'] == 'songofsolomon.json'
    assert book_info['matched']['name'] == 'Song of Solomon'
    assert book_info['matched']['order'] == 22
    assert book_info['extras'] == ['Authorized (King James) Version (AKJV)']

    book_info = get_book_info('invalid')
    assert book_info == None

    book_info = get_book_info('enoch')
    assert book_info['book'] == 'enoch'
    assert book_info['filename'] == 'enoch.json'
    assert book_info['matched']['name'] == 'Enoch'
    assert book_info['matched']['order'] == 67
    assert book_info['extras'] == ['Apocrypha']
