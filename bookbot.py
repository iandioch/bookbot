import json
from enum import Enum
from flask import Flask, request

app = Flask(__name__)
PAT = None
with open('config.priv.txt', 'r') as f:
    lines = f.readlines()
    PAT = lines[0].strip()
VERIFICATION_TOKEN = ''

MessageType = Enum('MessageType', ['TEXT', 'ERROR'])


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
            handle_message(None, message)
        except Exception as e:
            print('ERROR:', e)
    return 'ok'


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
        #TODO(iandioch): Handle quick replies.
        if 'text' in message:
            yield sender_id, {'type': MessageType.TEXT, 'message_id':message['mid'], 'data':message['text']}
        else:
            print('WARNING: Could not parse this kind of message.', message)
            yield sender_id, {'type': MessageType.ERROR, 'message_id':message['mid'], 'data':None}


def handle_message(user_id, message):
    if message is None:
        print('WARNING: Message is none.')
        return
    if message['type'] is MessageType.TEXT:
        print('INFO: Received message:', message['data'])
        return
    print('ERROR: Didn\'t recognise message type.', message)


if __name__ == '__main__':
    app.run(port=8767, debug=True)
