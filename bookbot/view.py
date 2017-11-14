import json

from tinydb import TinyDB, Query

from book import Book
from bookbot import send_message, get_user_info


db = TinyDB('data/users.priv.json')
User = Query()

# Quick Replies
QR_SEARCH_FOR_BOOK = 'Search for book'
QR_I_OWN_THIS_BOOK = 'I have a copy'
QR_VIEW_MY_BOOKS = 'View my books'


def create_quick_reply(s, payload=""):
    return {
        "content_type": "text",
        "title": s,
        "payload": payload,
    }


def create_quick_replies(lst, payload=""):
    quick_reply_objs = []
    for reply in lst:
        quick_reply_objs.append(create_quick_reply(reply, payload))
    return quick_reply_objs


class View:
    """A state within the user flow. Consists of a message,
    possibly including some Quick Replies."""

    message = "Default message"
    quick_replies = []

    @classmethod
    def show_info(cls, user_id, message_text, quick_reply_list):
        send_message(user_id, message_text, quick_reply_list)

    @classmethod
    def show(cls, user_id, payload=None):
        quick_reply_objs = create_quick_replies(cls.quick_replies)
        cls.show_info(user_id, cls.message, quick_reply_objs)


class StartView(View):
    """The view the user sees when they first message, or
    when they send an invalid message."""

    #TODO(iandioch): Show this view at first message.
    message = "Well lad wdc??"
    quick_replies = [QR_SEARCH_FOR_BOOK]


class BookSearchView(View):
    """A view in which a user types a book name to search for it."""

    message = "Please enter a search!"


class BookDetailView(View):
    """A view giving details about a particular book."""

    quick_replies = [QR_I_OWN_THIS_BOOK, QR_SEARCH_FOR_BOOK, QR_VIEW_MY_BOOKS]

    @classmethod
    def search(cls, user_id, query):
        book = Book.search_book(query)
        if book is None:
            message = 'No such book found!'
            cls.show_info(user_id, message, [])
            StartView.show(user_id)
        message = '*{}* ({})\n'.format(book.title, book.year)
        message += ', '.join('_{}_'.format(a) for a in book.authors)
        message += '\nISBN: `{}`'.format(book.isbn)

        print('INFO: Finding owners of book', book.isbn)
        owners = db.search(User.owns.any([book.isbn]))
        if len(owners) > 0:
            message += '\nThe following people own this book:'
            for owner in owners:
                info = get_user_info(owner['fb_id'])
                message += '\n{} {}'.format(info['first_name'], info['last_name'])
        payload = json.dumps({'book': {'isbn':book.isbn}})
        quick_reply_objs = create_quick_replies(cls.quick_replies, payload)
        cls.show_info(user_id, message, quick_reply_objs)

    @classmethod
    def show(user_id, payload):
        pass


class OwnBookView(View):
    """A view after a user says they own a copy of a book."""

    message = 'Ok!'
    quick_replies = [QR_VIEW_MY_BOOKS, QR_SEARCH_FOR_BOOK]

    @staticmethod
    def show(user_id, payload):
        print(payload)
        data = json.loads(payload)
        if 'book' not in data:
            print('ERROR: No "book" in payload.')
            super(OwnBookView, OwnBookView).show(user_id)
            return
        if 'isbn' not in data['book']:
            print('ERROR: No isbn in book in payload.')
            super(OwnBookView, OwnBookView).show(user_id)
            return
        users_data = db.search(User.fb_id == user_id)
        user_data = None
        if len(users_data) > 0:
            user_data = users_data[0]
        if user_data is None:
            user_data = {'fb_id': user_id}
            db.insert(user_data)
        if 'owns' not in user_data:
            user_data['owns'] = []
        user_data['owns'].append(data['book']['isbn'])
        db.update(user_data, User.fb_id == user_id)
        super(OwnBookView, OwnBookView).show(user_id)


class MyBooksView(View):
    """A view where a user can see a list of all of the
    books that they have a copy of."""

    quick_replies = [QR_SEARCH_FOR_BOOK]
    message = "You haven't marked any books as owned!"

    @staticmethod
    def show(user_id, payload):
        print('viewing books of', user_id)
        users = db.search(User.fb_id == user_id)
        books = []
        if len(users) > 0:
            user = users[0]
            if 'owns' in user:
                books = user['owns']

        if len(books) == 0:
            super(MyBooksView, MyBooksView).show(user_id)
            return

        message = ''
        for isbn in books:
            book = Book.search_book(isbn)
            message += '\n*{}* (ISBN `{}`)'.format(book.title, book.isbn)
        MyBooksView.show_info(user_id, message, create_quick_replies(MyBooksView.quick_replies))


view_triggers = {
        QR_SEARCH_FOR_BOOK: BookSearchView,
        QR_I_OWN_THIS_BOOK: OwnBookView,
        QR_VIEW_MY_BOOKS: MyBooksView,
}


def handle_view_flow(user_id, message):
    text = message['data']['text']
    if text in view_triggers:
        payload = None
        print('looking for payload')
        print(message)
        if 'quick_reply' in message['data'] and 'payload' in message['data']['quick_reply']:
            payload = message['data']['quick_reply']['payload']
        view_triggers[text].show(user_id, payload)
    else:
        BookDetailView.search(user_id, text)
