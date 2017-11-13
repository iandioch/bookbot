from book import Book
from bookbot import send_message

# Quick Replies
QR_SEARCH_FOR_BOOK = "Search for book"


def create_quick_reply(s, payload=""):
    return {
        "content_type": "text",
        "title": s,
        "payload": payload,
    }


def create_quick_replies(lst):
    quick_reply_objs = []
    for reply in lst:
        quick_reply_objs.append(create_quick_reply(reply))
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
    def show(cls, user_id):
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

    quick_replies = [QR_SEARCH_FOR_BOOK]

    @classmethod
    def search(cls, user_id, query):
        print(query)
        book = Book.search_book(query)
        message = '*{}*\n{}'.format(book.title, ', '.join('_{}_'.format(a) for a in book.authors))
        cls.show_info(user_id, message, create_quick_replies(cls.quick_replies))



view_triggers = {
        QR_SEARCH_FOR_BOOK: BookSearchView,
}


def handle_view_flow(user_id, message):
    if message['data'] in view_triggers:
        view_triggers[message['data']].show(user_id)
    else:
        BookDetailView.search(user_id, message['data'])
