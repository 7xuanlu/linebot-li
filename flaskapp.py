import sys
import datetime
from datetime import timedelta
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = '140.115.157.80'
app.config['MYSQL_DATABASE_USER'] = 'test'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
app.config['MYSQL_DATABASE_DB'] = 'test'
mysql.init_app(app)

line_bot_api = LineBotApi('fmkwUkq72NMO7Jwi/gcJ8knd4HtBttgRNYRgc24UqTAfmNpJwWib2mI+DCuyYS1BSgAsbk8XA6sRlGhrWfLjIsAcZrOiZ7ARMegGCBfalUYqLT7XV6O+cmMo/q3EiKvhC')
handler = WebhookHandler('8874e68d35e458b185feaba01398d8c5')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    dt = datetime.datetime.now().strftime('Y-%m-%d %H:%M:%S')
    conn = mysql.connect()
    c = conn.cursor()
    c.execute('INSERT INTO test (datetime, message) VALUES (%s, %s)', (dt, message))
    conn.commit()

if __name__ == '__main__':
    app.run()
