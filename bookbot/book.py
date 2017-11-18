import json
import re
import isbnlib


BOOK_SAVE_FILE_PATH = 'data/books.priv.json'
# A cache to stop repeat lookups of the same data.
isbn_to_book = {}


class Book:
    """An object containing data about a book."""

    def __init__(self):
        self.title: str = None
        self.authors: List[str] = []
        self.urls: List[str] = []
        self.year = '1000 A.D.'
        self.isbn = '123456789'
        pass

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def update(self, d):
        if 'title' in d:
            self.title = d['title']
        if 'authors' in d:
            self.authors = d['authors']
        if 'urls' in d:
            self.urls = d['urls']
        if 'year' in d:
            self.year = d['year']
        if 'isbn' in d:
            self.isbn = d['isbn']

    @staticmethod
    def search_book(query):
        if query in isbn_to_book:
            return isbn_to_book[query]
        results = isbnlib.goom(query)
        metadata = None
        if len(results) > 0:
            for result in results:
                if result['Language'] == 'en':
                    metadata = result
                    break
            if metadata is None:
                metadata = results[0]
        if metadata is None:
            print('WARNING: Book "{}" not found.'.format(query))
            return None
        
        book = Book()
        if 'Title' in metadata:
            book.title = metadata['Title']
        if 'Authors' in metadata:
            book.authors = []
            for auth in metadata['Authors']:
                book.authors.extend(re.split(r'[;,]', auth))
        if 'Year' in metadata:
            book.year = metadata['Year']
        if 'ISBN-13' in metadata:
            book.isbn = metadata['ISBN-13']

        isbn_to_book[book.isbn] = book
        save_books()
        return book


def load_books_from_file(filepath):
    d = {}
    with open(filepath, 'r') as f:
        data = json.load(f)
        for isbn in data:
            book = Book()
            book.update(data[isbn])
            d[isbn] = book
    return d


def load_books():
    print('INFO: Loading books from file.')
    global isbn_to_book
    try:
        isbn_to_book = load_books_from_file(BOOK_SAVE_FILE_PATH)
    except Exception as e:
        print('ERROR:', e)


def save_books():
    print('INFO: Saving books to file.')
    data = {}
    for isbn in isbn_to_book:
        data[isbn] = isbn_to_book[isbn].__dict__
    with open(BOOK_SAVE_FILE_PATH, 'w+') as f:
        f.write(json.dumps(data))
