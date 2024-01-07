from flask import Flask, request, abort, render_template
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import PostbackAction,URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate, LocationSendMessage, MessageTemplateAction
import os
import json
from datetime import datetime, timedelta

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
    if event.message.text == "找機車":
        # Get the required token
        get_token = "https://smart-campus.kits.tw/api/api/account/login"
        data = {'email':'bachelor_07',
                'password':'bachelor_07'}
        response = requests.post(get_token, data)
        token = response.json()["token"]

        # Get GPS data from sensor id
        headers = {'token':token, 
                   'Content-Type': 'application/json'}
        sensor_id = "df11640a-35f9-4f2b-abae-0016cfac40ba"
        get_gps_api = "https://smart-campus.kits.tw/api/api/sensors/GPS/" + sensor_id

        try:
            response = requests.get(url=get_gps_api, headers=headers)
            # 4038 gps data
            gps_data = response.json()[-1]["value"]
            gps_data = hex(gps_data)

            # 4038 timestamp
            time = response.json()[-1]["timestamp"]
            time = datetime.fromtimestamp(time / 1000) + timedelta(hours=8)
            time = str(time)
            time = "最後紀錄時間: " + time[:len(time)-7]

            latitude, longtitude = gps_data[2:9], gps_data[9:]
            latitude = int(latitude, 16) * (10 ** (-7))
            longtitude = int(longtitude, 16) * (10 ** (-7))
            #str_latitude = str(latitude)
            #str_longtitude = str(longtitude)
            #LocationLink =  "https://www.google.com/maps/search/?api=1&query="+str_latitude+","+str_longtitude
            location_message = LocationSendMessage(title="機車定位", address=time, latitude=latitude, longitude=longtitude)
            line_bot_api.reply_message(event.reply_token, location_message)

        except requests.exceptions.RequestException as e:
            message = TextSendMessage(text="Enable to fetch gps from api!!!")
            line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "PPT":
        ppt_message = TextSendMessage(text="PPT link: [Link Text](https://docs.google.com/presentation/d/1LRZklWsZZbCR0RZvv2ahiGYByEnm5q6ntlfJr1miSaU/edit?usp=sharing)")
        line_bot_api.reply_message(event.reply_token, ppt_message)
        
    else:
        buttons_template = ButtonsTemplate(
            title='看來是又忘記機車停在哪了:)',
            text='Please select an option:',
            actions=[
                MessageTemplateAction(
                    label='找機車',
                    text='找機車'
                ),
                URIAction(
                    label='PPT',
                    uri='https://docs.google.com/presentation/d/1LRZklWsZZbCR0RZvv2ahiGYByEnm5q6ntlfJr1miSaU/edit?usp=sharing'
                )
            ]
        )
        # Send the button template as a reply
        template_message = TemplateSendMessage(alt_text='Buttons Template', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

