import json
import re
import isbnlib


# A cache to stop repeat lookups of the same data.
isbn_to_book = {}


class BookSource:
    """Somewhere this book can be found. Eg. A specific library, a person, or a URL."""

    def __init__(self):
        pass

    def is_available(self):
        return False


class Book:
    """An object containing data about a book."""

    def __init__(self):
        self.title: str = None
        self.authors: List[str] = []
        self.year = '1000 A.D.'
        self.isbn = '123456789'
        self.sources: List[BookSource] = []
        pass

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def search_book(query):
        if query in isbn_to_book:
            return isbn_to_book[query]
        results = isbnlib.goom(query)
        metadata = None
        if len(results) > 0:
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
        return book
