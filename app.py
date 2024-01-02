from flask import Flask, request, abort, render_template
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import json

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# @app.route("/")
# def get_data():
#     headers = {'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imdyb3VwMSIsInV1aWQiOiJlYTcyNDI0MC04OTI2LTQwMTAtYjljZS1mNzM0YzE1ZmNjN2IiLCJuYW1lIjoiZ3JvdXAxIiwiaWF0IjoxNzAzNjc4NTY3LCJleHAiOjE3MDM3NjQ5Njd9._pOXTF6RmiBWMZrloLwCqquTSS4zT5n6NCaIJLvIhx0',
#     'Content-Type': 'application/json'}
#     response = request.get_json('https://smart-campus.kits.tw/api/api/sensors/BATTERY_VOLTAGE/8fd928dc-b2b1-4efd-a5d1-8087f62bb0ab', headers=headers)
#     response = "I'm API :D"

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
    headers = {'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJhY2hlbG9yXzA3IiwidXVpZCI6ImFiZDMyMjhkLThmNWQtNDJmMS1hODY4LWIwODA0OTUzMTg1ZiIsIm5hbWUiOiJiYWNoZWxvcl8wNyIsImlhdCI6MTcwNDAxMzk3NSwiZXhwIjoxNzExNzg5OTc1fQ.6uHLdlUAWQ_RsaEW9ERMU_EEB9_mbB83pww_cvfNLm0',
    'Content-Type': 'application/json'}

    # Get GPS data from sensor id
    sensor_id = "df11640a-35f9-4f2b-abae-0016cfac40ba"

    get_gps_api = "https://smart-campus.kits.tw/api/api/sensors/GPS/" + sensor_id
    response = requests.get(url=get_gps_api, headers=headers)

    gps_data = response.json()[0]["value"]
    gps_data = hex(gps_data)

    latitude, longtitude = gps_data[2:9], gps_data[9:]

    latitude = int(latitude, 16) * (10 ** (-7))
    longtitude = int(longtitude, 16) * (10 ** (-7))
    print(f"Latitude: {latitude}, Longtitude: {longtitude}")
    # sensorId = response.get('sensorId', None) # 解析資料，若不是 JSON，則返回 None
    # value = response.get('value', None)
    # result = f'Hello {sensorId},{value}'

    # message = TextSendMessage(text=event.message.text)
    message = TextSendMessage(text=response.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

