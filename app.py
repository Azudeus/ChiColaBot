# encoding: utf-8
from flask import Flask, request, abort
import requests
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('ulnphNOuEmnoh2thksT1pvCnvm5hJ4H2EuwwCZd/3AvvEihFLu1w7wdSS+mnl4ZH4+8tb+O0KFEtwGuxwFD8dLwYs/k4daCh3x774a6NwsEAXXX4SnYLJJZFYECDSpPVIUSNaD9+6SxyIgapGgmNpwdB04t89/1O/w1cDnyilFU=') #Your Channel Access Token
handler = WebhookHandler('488e36b743ec757a4e7843d9022d3259') #Your Channel Secret
fixer_key = '3befaf87f682bd0c9be237d609e6f4ba'

@app.route('/')
def index():
	return 'Yo, its working!'

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
def handle_text_message(event):
    text = handle_pattern(event.message.text.lower()) #message from user

    if (len(text)>0):
	    line_bot_api.reply_message(
	        event.reply_token,
	        TextSendMessage(text=text)) #reply the same message from user

def handle_pattern(text):
	try:
		keyword = text.split(' ')[0]
		value = text.split(' ')[1]
		ret = {
			'tax': str(int(float(value)*110/100)),
			'serv': str(int(float(value)*105*110/10000)),
			'service': str(int(float(value)*105*110/10000)),
			'sum': handle_sum(text),
			'conv': handle_convert(text),
			'convert': handle_convert(text)
		}.get(keyword, '')
	except (ValueError, IndexError) as e:
		ret = ''

	return ret

def handle_sum(text):
	total = 0.0;
	arr = text.split(' ')
	for i in range(len(arr)):
		if (check_float(arr[i])):
			total += (float(arr[i]))
	return str(int(total))

def handle_convert(text):
	arr = text.split(' ')
	req = requests.get('http://data.fixer.io/api/latest?access_key='+fixer_key)
	reqjson = req.json()
	return str(rate)

	try:
		curr1 = arr[1].upper()
		curr2 = arr[2].upper()
		value = arr[3]

		rate = float(reqJson['rates'][curr1] / reqJson['rates'][curr2])
		ret = 'Rate from '+curr1+' to '+curr2+' = '+str(round(rate,3))
		if check_float(value):
			result = value*rate
			ret += '\n'
			ret += value+' '+curr1+' = '+str(round(result,2))+' '+curr2			
	except (ValueError, IndexError) as e:
		ret = ''

def check_float(text):
	try:
		float(text)
		return True
	except (ValueError) as e:
		return False

if __name__ == "__main__":
	app.run()