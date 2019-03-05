import os, json
import mysql.connector
from datetime import datetime
# loop through all the files
#for f in os.listdir('message'):
#     (blablahbla, filename, foo)

cnx = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='test')
cursor = cnx.cursor(buffered=True)

with open("/var/www/flask/message/2019-01-02.json") as fin:
    data = json.load(fin)
    for i, v in enumerate(data["message"]):
        time = datetime.fromtimestamp(v["time"]/1000)
        if(v["type"]=="text"):
            add_text = ("INSERT INTO test3 "
                        "(timestamp, type, text) "
                        "VALUES (%s, %s, %s)")
            message = (time, v["type"], v["text"])
            cursor.execute(add_text, message)
        else:
            add_image = ("INSERT INTO test3 "
                        "(timestamp, type, ipath) "
                        "VALUES (%s, %s, %s)")
            message = (time, v["type"], v["ipath"])
            cursor.execute(add_image, message)
    #print(json.dumps(data, indent=4, sort_keys=True))
    
cnx.commit()

cursor.close()
cnx.close()
