from bookbot import send_message

# Quick Replies
QR_SEARCH_FOR_BOOK = "Search for book"


def create_quick_reply(s, payload=""):
    return {
        "content_type": "text",
        "title": s,
        "payload": payload,
    }


class View:
    """A state within the user flow. Consists of a message,
    possibly including some Quick Replies."""

    message = "Default message"
    quick_replies = []

    @classmethod
    def show(cls, user_id):
        quick_reply_objs = []
        for reply in cls.quick_replies:
            quick_reply_objs.append(create_quick_reply(reply))
        send_message(user_id, cls.message, quick_reply_objs)



class StartView(View):
    """The view the user sees when they first message, or
    when they send an invalid message."""

    message = "Well lad wdc??"
    quick_replies = [QR_SEARCH_FOR_BOOK]


class BookSearchView(View):
    """A view in which a user types a book name to search for it."""

    message = "Please enter a search!"


class BookDetailView(View):
    """A view giving details about a particular book."""



view_triggers = {
        QR_SEARCH_FOR_BOOK: BookSearchView,
}


def handle_view_flow(user_id, message):
    if message['data'] in view_triggers:
        view_triggers[message['data']].show(user_id)
    else:
        StartView.show(user_id)
