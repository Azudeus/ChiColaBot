# encoding: utf-8
from flask import Flask, request, abort
from bs4 import BeautifulSoup
import requests
import json
import sys
import random
import os

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

line_bot_api = LineBotApi(os.environ['LINE_BOT_TOKEN']) #Your Channel Access Token
handler = WebhookHandler(os.environ['CHANNEL_SECRET']) #Your Channel Secret
fixer_key = os.environ['FIXER_KEY']

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
		elif keyword == 'horrib':
			ret = handle_horrib()
		elif keyword == 'tes':
			ret = handle_test()
		elif keyword == 'test':
			ret = handle_test()
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
	encoded_text = ('{"search": "' + text + '"}').encode('utf-8')
	req = requests.post('http://gbf.gw.lt/gw-guild-searcher/search', data = encoded_text)
	if (req.status_code >= 400):
		return ''
	else:
		reqJson = req.json()
		ret = ''
		max = len(reqJson['result'])
		if (max > 3):
			max = 3
		for i in range(0, max):
			for key in reqJson['result'][i]['data']:
				if (key['is_seed'] == 1):
					seed = 'True'
				else:
					seed = 'False'
				ret = ret + key['name'] + ' - GW:' + str(key['gw_num']) + ' - Rank:' + str(key['rank']) + ' - pts:' + str(key['points']) + ' - seed:' + seed + '\n'
			ret = ret + '\n'
		return ret

def handle_horrib():
	ret = ''
	r  = requests.get("http://horriblesubs.info/")

	data = r.text

	soup = BeautifulSoup(data, "lxml")
	schedule = soup.find("table", {"class": "schedule-table"})
	for show in schedule:
		pdt_time = show.find('td',{"class": "schedule-time"}).contents[0]
		wib_time = conv_pdt_to_wib(pdt_time)
		ret = ret + show.find('a').contents[0] + ' ' + wib_time + ' WIB\n'
	return ret
	
def conv_pdt_to_wib(pdt_time):
	# could maybe use this instead https://docs.python.org/2/library/datetime.html#time-objects
	pdt_hour = pdt_time.split(':')[0]
	pdt_min = pdt_time.split(':')[1]

	wib_hour = (int(pdt_hour) + 14) % 24
	wib_time = str(wib_hour) + ':' + pdt_min
	return wib_time

def handle_test():
	ret_texts = ["masuk", "masuk pak eko", "ga masuk", "dikit lagi", "sayang sekali", "nyaris gan", "masuk tapi gagal", "no response, it's just a corpse", "mau masuk tapi gagal", "akan masuk", "bentar lagi masuk", "masuk sempurna", "fertilized", "ga muat", "ga sempet masuk", "masuk tapi keluar lagi", "ga jadi masuk", "denied", "bukan aan ya kamu", "kuy sudirman", "bentar lagi baru masuk", "no message found", "404 error", "malah kuda yang masuk"]
	ret = "masuk" if random.getrandbits(1) else random.choice(ret_texts)
	return ret

def check_float(text):
	try:
		float(text)
		return True
	except (ValueError) as e:
		return False

if __name__ == "__main__":
	app.run()