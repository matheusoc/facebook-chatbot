import os
from flask import Flask, request
import constants
import json
import requests
import traceback

api_key = constants.WEATHER_KEY

# coding: utf-8

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            data = json.loads(request.data.decode())
            print(data)
            message = data['entry'][0]['messaging'][0]['message']
            sender = data['entry'][0]['messaging'][0]['sender']['id']  # Sender ID
            if 'attachments' in message:
                if 'payload' in message['attachments'][0]:
                    if 'coordinates' in message['attachments'][0]['payload']:
                        location = message['attachments'][0]['payload']['coordinates']
                        latitude = location['lat']
                        longitude = location['long']

                        url = 'http://api.openweathermap.org/data/2.5/weather?' \
                              'lat={}&lon={}&appid={}&units={}&lang={}'.format(latitude, longitude, api_key, 'metric',
                                                                               'pt')
                        r = requests.get(url)

                        description = r.json()['weather'][0]['description'].title()
                        icon = r.json()['weather'][0]['icon']
                        weather = r.json()['main']
                        text_res = ('{}\n' \
                                   'Temperatura: {}\n' \
                                   'Pressao: {}\n' \
                                   'Humidade: {}\n' \
                                   'Maxima: {}\n' \
                                   'Minima: {}').format(unicode(description).encode('utf-8'),
                                                        unicode(weather['temp']).encode('utf-8'),
                                                        unicode(weather['pressure']).encode('utf-8'),
                                                        unicode(weather['humidity']).encode('utf-8'),
                                                        unicode(weather['temp_max']).encode('utf-8'),
                                                        unicode(weather['temp_min']).encode('utf-8')
                                                        )
                        payload = {'recipient': {'id': sender}, 'message': {'text': text_res}}
                        r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' +
                                          constants.FACEBOOK_TOKEN,
                                          json=payload)
            else:
                text = message['text']
                payload = location_quick_reply(sender)
                r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + constants.FACEBOOK_TOKEN,
                                  json=payload)
        except Exception as e:
            print(traceback.format_exc())
    elif request.method == 'GET':
        if request.args.get('hub.verify_token') == constants.FACEBOOK_VERIFY:
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    return "Nothing"

def location_quick_reply(sender):
    return {
        "recipient": {
            "id": sender
        },
        "message": {
            "text": "Compartilhe sua localizacao:",
            "quick_replies": [
                {
                    "content_type": "location",
                }
            ]
        }
    }

if __name__ == '__main__':
    app.run(debug=True)