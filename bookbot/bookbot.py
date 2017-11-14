import json
import requests
from enum import Enum
from flask import Flask, request

import view
from book import Book

SEND_MESSAGE_URL = 'https://graph.facebook.com/v2.6/me/messages'
USER_INFO_URL = 'https://graph.facebook.com/v2.6/'

app = Flask(__name__)
PAT = None
with open('config.priv.txt', 'r') as f:
    lines = f.readlines()
    PAT = lines[0].strip()
VERIFICATION_TOKEN = ''

MessageType = Enum('MessageType', ['TEXT', 'ERROR', 'QUICK_REPLY'])


# Authentification with Facebook
@app.route('/', methods=['GET'])
def root():
    if request.args.get('hub.verify_token', '') == VERIFICATION_TOKEN:
        print('INFO: Verification complete')
        return request.args.get('hub.challenge', '')
    else:
        print('WARNING: Wrong verification token.')
        return 'Wrong verification tokey toke.'


@app.route('/', methods=['POST'])
def root_postauth():
    payload = request.get_data().decode('utf-8')
    data = parse_request_data(payload)
    for user_id, message in data:
        try:
            handle_message(user_id, message)
        except Exception as e:
            print('ERROR:', e)
    return 'ok'


def send_message(user_id, text, quick_replies=[]):
    if len(quick_replies) == 0:
        quick_replies = None
    r = requests.post(SEND_MESSAGE_URL,
            params={'access_token':PAT},
            data=json.dumps({
                'recipient': {'id':user_id},
                'message': {'text': text, 'quick_replies': quick_replies } 
            }),
            headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print('WARNING:', r.text)


def get_user_info(user_id):
    params = {'fields':'first_name, last_name', 'access_token':PAT}
    r = requests.get(USER_INFO_URL + user_id, params=params)
    if r.status_code != requests.codes.ok:
        print('WARNING:', r.text)
        return None
    return json.loads(r.text)


def parse_request_data(payload):
    data = json.loads(payload)
    events = data['entry'][0]['messaging']
    for event in events:
        sender_id = event['sender']['id']
        if 'message' not in event:
            print('ERROR: Could not parse event..', event)
            yield sender_id, None
        message = event['message']
        #TODO(iandioch): Handle attachments.
        if 'quick_reply' in message:
            yield sender_id, {'type': MessageType.QUICK_REPLY, 'message_id': message['mid'], 'data': message}
        elif 'text' in message:
            yield sender_id, {'type': MessageType.TEXT, 'message_id':message['mid'], 'data': message}
        else:
            print('WARNING: Could not parse this kind of message.', message)
            yield sender_id, {'type': MessageType.ERROR, 'message_id':message['mid'], 'data':None}


def handle_message(user_id, message):
    if message is None:
        print('WARNING: Message is none.')
        return
    if message['type'] is MessageType.TEXT or message['type'] is MessageType.QUICK_REPLY:
        print('INFO: Received message:', message['data'])
        view.handle_view_flow(user_id, message)
        return
    print('ERROR: Didn\'t recognise message type.', message)


if __name__ == '__main__':
    app.run(port=8767, debug=True)
