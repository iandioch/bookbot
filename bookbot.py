import json
from flask import Flask, request

app = Flask(__name__)
PAT = None
with open('config.priv.txt', 'r') as f:
    lines = f.readlines()
    PAT = lines[0].strip()
VERIFICATION_TOKEN = ''

# Authentification with Facebook
@app.route('/', methods=['GET'])
def root():
    if request.args.get('hub.verify_token', '') == VERIFICATION_TOKEN:
        print('Verification complete')
        return request.args.get('hub.challenge', '')
    else:
        print('Wrong verification token.')
        return 'Wrong verification tokey toke.'


@app.route('/', methods=['POST'])
def root_postauth():
    payload = request.get_data().decode('utf-8')
    data = parse_request_data(payload)
    print(payload)
    for message in data:
        print(message)
    return 'ok'


def parse_request_data(payload):
    data = json.loads(payload)
    events = data['entry'][0]['messaging']
    for event in events:
        sender_id = event['sender']['id']
        if 'message' not in event:
            yield sender_id, None
        message = event['message']
        #TODO(iandioch): Handle attachments.
        #TODO(iandioch): Handle quick replies.
        if 'text' in message:
            yield sender_id, {'type':'text', 'message_id':message['mid'], 'data':message['text']}
        else:
            yield sender_id, {'type':'error', 'message_id':message['mid'], 'data':None}




if __name__ == '__main__':
    app.run(port=8767)
