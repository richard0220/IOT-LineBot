from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import json

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/callback")
def get_data():
    headers = {'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imdyb3VwMSIsInV1aWQiOiJlYTcyNDI0MC04OTI2LTQwMTAtYjljZS1mNzM0YzE1ZmNjN2IiLCJuYW1lIjoiZ3JvdXAxIiwiaWF0IjoxNzAzNjc4NTY3LCJleHAiOjE3MDM3NjQ5Njd9._pOXTF6RmiBWMZrloLwCqquTSS4zT5n6NCaIJLvIhx0',
    'Content-Type': 'application/json'}
    # response = request.get('https://smart-campus.kits.tw/api/api/sensors/BATTERY_VOLTAGE/8fd928dc-b2b1-4efd-a5d1-8087f62bb0ab', headers=headers)
    response = "I'm API :D"
    return response

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    # message = get_data()
    line_bot_api.reply_message(event.reply_token, get_data())

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)