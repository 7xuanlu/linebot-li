import json, os
import numpy as np
from datetime import date, datetime

import jieba.analyse
import re

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

line_bot_api = LineBotApi('XNfPf1f8R5lAlZMy49o0iVEaW0J7REURi8sQ8vpT6voY0s84f8Qwqg3rZyyXKxqXdYXjEg1NW+lBnoIB6VfPl+yKvbHO29EmujsYs9XYnaEJFnKa67fbzIGtxPGuc2fAdhMUx+ffLmT0Omb2lNg/mgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d2c493d92a8fc3a7fe31ad9552c105ec')


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
    # get user profiles, so that we could then store the user names
    try:
        gid = event.source.group_id
        uid = event.source.user_id 
        profile = line_bot_api.get_group_member_profile(gid, uid)
        time = datetime.now()
        text = event.message.text
        fpath = "/var/www/flask/message/" + time.strftime("%Y-%m-%d") + ".json"
     
        if os.path.isfile(fpath):
            with open(fpath) as fin:
                data = json.load(fin)
                data[event.timestamp] = {
                    "type": "text",
                    "user": profile.display_name,
                    "text": text
                }
                with open(fpath, "w") as fout:
                    json.dump(data, fout, ensure_ascii=False, indent=4)
        else:
            data = {}
            data[event.timestamp] = {
                "type": "text",
                "user": profile.display_name,
                "text": text
            }
            with open(fpath, "w") as fout:
                json.dump(data, fout, ensure_ascii=False, indent=4)
    except:
        jieba.set_dictionary("/var/www/flask/model/extra_dict/dict.txt.big")
        jieba.load_userdict("/var/www/flask/userdict.txt") # 用來抓出特定字詞當tag
        jieba.analyse.set_stop_words("/var/www/flask/stop_words.txt") # 防止抓出特定字詞

        uid = event.source.user_id
        profile = line_bot_api.get_profile(uid)
        date = datetime.now().strftime("%Y-%m-%d")
        fpath = "/var/www/flask/message/" + date + ".json"
        plus = set(line.strip() for line in open('/var/www/flask/plus.txt', encoding="utf-8"))

        with open(fpath, encoding="utf-8") as fin:
            data = json.load(fin)
            purchase_record = {}
            with open("/var/www/flask/product_list.txt", encoding="utf-8") as fin:
                product_list = fin.read().splitlines()
                for record in data:
                    obj = data[record]  # obj is object in dictionary
                    if obj["type"]=="text":
                        if obj["user"] == "莊雅萍":
                            #print(obj["text"] + "\n")
                            temp = obj["text"].split("\n")
                            for i in temp:
                                tags = jieba.analyse.extract_tags(i)
                            for tag in tags:
                                if tag not in plus:
                                    product_list.append(tag)
                        else:
                            tags = jieba.analyse.extract_tags(obj["text"])
                            for tag in tags:
                                if tag not in plus:
                                    product_list.append(tag)
                                else:
                                    for i in tag:
                                        if i.isdigit():
                                            amount = i
                                    for tag in tags:
                                        if tag in product_list:
                                            if purchase_record.get(tag):
                                                purchase_record[tag] += amount
                                            else:
                                                purchase_record[tag] = amount
                    else:
                        pass
            purchase_record = json.dumps(purchase_record, ensure_ascii=False, indent=4).strip("{}")
            message = "{}, 您好!\n以下是{}的購買紀錄:\n{}".format(profile.display_name, date, purchase_record)
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text=message))

# handle image message
@handler.add(MessageEvent, message=ImageMessage)
def get_content(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    time = datetime.now()
    gid = event.source.group_id
    uid = event.source.user_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    fpath = "/var/www/flask/message/" + time.strftime("%Y-%m-%d") + ".json"
    ipath = "/var/www/flask/image/" + time.strftime('%Y-%m-%d %H:%M:%S') + ".png"
    
    with open(ipath, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    if os.path.isfile(fpath):
        with open(fpath) as fin:
            data = json.load(fin)
            data[event.timestamp] = {
                "type": "image",
                "user": profile.display_name,
                "ipath": ipath
            }
            with open(fpath, "w") as fout:
                json.dump(data, fout, ensure_ascii=False, indent=4)
    else:
        data = {}
        data[event.timestamp] = {
            "type": "image",
            "user": profile.display_name,
            "ipath": ipath
        }
        with open(fpath, "w") as fout:
             json.dump(data, fout, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    app.run()
