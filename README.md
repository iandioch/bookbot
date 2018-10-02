This is Bookbot, a Messenger bot to handle the sharing and tracking of books.

It was built with the help of [this example](https://github.com/hungtraan/FacebookBot-echobot-simple).

# Running

`python3 -m pip install -r requirements.txt` will install dependencies.

Copy `config.priv.json.example`. Modify the `pat` field to include your Page Access Token and save the file in the `bookbot` directory as `config.priv.json`

You can then run the bot with `python3 bookbot.py` from the `bookbot` directory. It will run on port `8767` by default. This port can be changed in the `config.priv.json` file.
