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
	arr = "conv JPY IDR 50".split(' ')
	req = requests.get('http://data.fixer.io/api/latest?access_key='+fixer_key)
	reqJson = req.json()

# {"success":true,"timestamp":1522685943,"base":"EUR","date":"2018-04-02","rates":{"AED":4.516368,"AFN":85.034725,"ALL":129.427713,"AMD":589.721637,"ANG":2.189045,"AOA":263.557227,"ARS":24.728317,"AUD":1.606251,"AWG":2.188891,"AZN":2.089898,"BAM":1.959428,"BBD":2.459428,"BDT":101.943292,"BGN":1.952054,"BHD":0.463358,"BIF":2153.204572,"BMD":1.229714,"BND":1.618915,"BOB":8.436356,"BRL":4.078102,"BSD":1.229714,"BTC":0.000175,"BTN":80.054378,"BWP":11.716591,"BYN":2.410426,"BYR":24102.394139,"BZD":2.456721,"CAD":1.588766,"CDF":1925.115495,"CHF":1.175533,"CLF":0.027337,"CLP":744.800849,"CNY":7.720638,"COP":3437.542358,"CRC":691.283747,"CUC":1.229714,"CUP":32.587421,"CVE":110.32994,"CZK":25.373302,"DJF":217.450327,"DKK":7.454194,"DOP":60.747873,"DZD":140.114844,"EGP":21.643229,"ERN":18.433722,"ETB":33.472813,"EUR":1,"FJD":2.48354,"FKP":0.873221,"GBP":0.876356,"GEL":2.956718,"GGP":0.876413,"GHS":5.424277,"GIP":0.873587,"GMD":57.894937,"GNF":11061.277296,"GTQ":9.021222,"GYD":251.144483,"HKD":9.651214,"HNL":28.958543,"HRK":7.409521,"HTG":79.09538,"HUF":312.77776,"IDR":16909.797031,"ILS":4.322321,"IMP":0.876413,"INR":80.122379,"IQD":1455.98136,"IRR":46413.094607,"ISK":121.065338,"JEP":0.876413,"JMD":153.738839,"JOD":0.871247,"JPY":130.402559,"KES":123.577416,"KGS":84.06202,"KHR":4911.354571,"KMF":489.610616,"KPW":1106.742958,"KRW":1297.987732,"KWD":0.368336,"KYD":1.008713,"KZT":392.782949,"LAK":10180.802103,"LBP":1856.867891,"LKR":191.220456,"LRD":162.014483,"LSL":14.535,"LTL":3.749033,"LVL":0.763099,"LYD":1.630847,"MAD":11.324561,"MDL":20.183302,"MGA":3910.490852,"MKD":61.264396,"MMK":1636.749373,"MNT":2935.327113,"MOP":9.932521,"MRO":431.630036,"MUR":40.949475,"MVR":19.146935,"MWK":877.339459,"MXN":22.520613,"MYR":4.748538,"MZN":75.320241,"NAD":14.552415,"NGN":436.548804,"NIO":38.059649,"NOK":9.696602,"NPR":128.094022,"NZD":1.703895,"OMR":0.473317,"PAB":1.229714,"PEN":3.964592,"PGK":3.995954,"PHP":64.154176,"PKR":141.908997,"PLN":4.212141,"PYG":6803.26954,"QAR":4.475914,"RON":4.658651,"RSD":117.690643,"RUB":70.831523,"RWF":1036.562802,"SAR":4.611181,"SBD":9.566685,"SCR":16.552243,"SDG":22.199045,"SEK":10.318296,"SGD":1.614221,"SHP":0.873583,"SLL":9567.174997,"SOS":692.328314,"SRD":9.13674,"STD":24514.225834,"SVC":10.760049,"SYP":633.278084,"SZL":14.588081,"THB":38.367078,"TJS":10.837841,"TMT":4.193325,"TND":2.950329,"TOP":2.720493,"TRY":4.88738,"TTD":8.152389,"TWD":35.810512,"TZS":2768.085992,"UAH":32.120131,"UGX":4531.495918,"USD":1.229714,"UYU":34.837773,"UZS":9985.277332,"VEF":60690.694939,"VND":28026.411471,"VUV":132.190926,"WST":3.151637,"XAF":655.658895,"XAG":0.074117,"XAU":0.000918,"XCD":3.313572,"XDR":0.845518,"XOF":655.658895,"XPF":119.374671,"YER":307.305518,"ZAR":14.588953,"ZMK":11068.879627,"ZMW":11.59629,"ZWL":396.404466}}

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
	except (ValueError, IndexError) as e:
		ret = e

	return ret

	# return 'Yo, its working!'

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
	reqJson = req.json()
	ret = ''

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
	except (ValueError, IndexError) as e:
	    app.logger.info("log: "+e)

	return ret

def check_float(text):
	try:
		float(text)
		return True
	except (ValueError) as e:
		return False

if __name__ == "__main__":
	app.run()