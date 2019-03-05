import datetime
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('84zaCoj2KWe4P8rQ0/EvRZC/sVZYHNhBtmrUnMqUjr6iLFwntfXOCEAs13LV6HQd1o6cSy7LPwsmv8qMYJdzfe0piNTH0pd/wHMVnPt6jhgqw9SkkJ6Ser5lzyBsJoezLS03BCcPpk3GC+wgB3pMDQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('902da4a0ee469a7ce951b15855ca8420')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    time = datetime.datetime.fromtimestamp(event.timestamp/1000.0).strftime('%Y-%m-%d %H:%M:%S')
    profile = line_bot_api.get_profile(event.source.user_id)
    
    with open('/var/www/flask/message.txt', 'a+') as m:
        m.write(time + ' ' + profile.display_name + ': ' +  event.message.text + '\n')

# handle image message
@handler.add(MessageEvent, message=ImageMessage)
def get_content(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    time = datetime.datetime.fromtimestamp(event.timestamp/1000.0).strftime('%Y-%m-%d %H:%M:%S')

    with open('/var/www/flask/image/' + time + '.png', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

if __name__ == "__main__":
    app.run()
