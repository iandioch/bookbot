import json


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
        self.sources: List[BookSource] = []
        self.sources.append('hi')
        pass

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def search_book(query):
        book = Book()
        book.title = "random title"
        book.authors = ['not a real author']
        return book
