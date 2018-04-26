# encoding: utf-8
from flask import Flask, request, abort
import requests
import json
import sys
import random

from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
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
		message_reply = TextSendMessage(text=text)
		if (text == 'tsukkomi'):
			message_reply = ImageSendMessage(
				original_content_url='https://media.tenor.com/images/d85d3a03369bdd47b87ff4dc5c803a66/tenor.gif',
				preview_image_url='https://media.tenor.com/images/d85d3a03369bdd47b87ff4dc5c803a66/tenor.gif'
			)
		line_bot_api.reply_message(
			event.reply_token,
			message_reply) #reply the same message from user

def handle_pattern(text):
	ret = ''
	try:
		keyword = text.split(' ')[0]
		if keyword == 'tax':
			value = text.split(' ')[1]
			ret = str(int(float(value)*110/100))
		elif keyword == 'serv' or keyword == 'service':
			value = text.split(' ')[1]
			ret = str(int(float(value)*105*110/10000))
		elif keyword == 'sum':
			ret = handle_sum(text)
		elif keyword == 'conv' or keyword == 'convert':
			ret = handle_convert(text)
		elif keyword == 'jpytoidr':
			value = text.split(' ')[1]
			ret = handle_convert_jpy_idr(value)
		elif keyword == 'choose':
			ret = handle_choose(text)
		elif keyword == 'rng':
			ret = handle_rng(text)
		elif keyword == 'gbfgwsearch':
			value = text.split(' ')[1]
			ret = handle_gbf_gw_search(value)
		elif keyword == 'tsukkomi':
			ret = 'tsukkomi'
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
	reqJson = req.json()
	try:
		curr1 = arr[1].upper()
		curr2 = arr[2].upper()
		value = arr[3]
		rate = float(reqJson['rates'][curr2] / reqJson['rates'][curr1])
		ret = 'Rate from '+curr1+' to '+curr2+' = '+str(round(rate,3))
		if check_float(value):
			result = float(value)*rate
			ret += '\n'
			ret += value+' '+curr1+' = '+str(round(result,2))+' '+curr2
	except (ValueError, IndexError, KeyError) as e:
		ret = 'Converter error'
	return ret

def handle_convert_jpy_idr(text):
	if check_float(text):
		req = requests.get('http://data.fixer.io/api/latest?access_key='+fixer_key+'&symbols=IDR,JPY')
		reqJson = req.json()
		rate = float(reqJson['rates']['IDR'] / reqJson['rates']['JPY'])
		ret = 'Rate from JPY to IDR = '+str(round(rate,3))
		result = float(text)*rate
		ret += '\n'
		ret += text+' JPY = '+str(round(result,2))+' IDR'
	else:
		ret = ''
	return ret

def handle_choose(text):
	if (len(text) > 500):
		ret = 'Choices is too long'
	else:
		text = text.replace('choose ','',1)
		arr = text.split(',')
		for i in range(len(arr)):
			arr[i] = arr[i].strip()
		ret = random.choice(arr)
	return ret
	
def handle_rng(text):
	arr = text.split(' ')
	if (int(arr[1]) < int(arr[2])+1):
		return str(random.randrange(int(arr[1]),int(arr[2])+1))
	else:
		return ''
		
def handle_gbf_gw_search(text):
	#Using http://gbf.gw.lt
	req = requests.post('http://gbf.gw.lt/gw-guild-searcher/search', data = '{"search": "' + text + '"}')
	if (req.status_code >= 400):
		return ''
	else:
		reqJson = req.json()
		ret = ''
		for crew in reqJson['result']:
			for key in crew['data']:
				if (key['is_seed'] == 1):
					seed = 'True'
				else:
					seed = 'False'
				ret = ret + key['name'] + ' - GW:' + str(key['gw_num']) + ' - Rank:' + str(key['rank']) + ' - pts:' + str(key['points']) + ' - seed:' + seed + '\n'
			ret = ret + '\n'
		return ret

def check_float(text):
	try:
		float(text)
		return True
	except (ValueError) as e:
		return False

if __name__ == "__main__":
	app.run()