import os
import traceback
from flask import Flask, request, abort, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from urllib import request as rq
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import *

import xun_op
import xun_ptt_notify

app = Flask(__name__)
sched = BackgroundScheduler()
xun_ptt_notify = xun_ptt_notify.xun_ptt_notify()

# Channel Access Token
line_bot_api = LineBotApi(os.environ['LINE_BOT_CHANNEL_TOKEN'])
# Channel Secret
handler = WebhookHandler(os.environ['LINE_BOT_CHANNEL_SECRET'])

# 監聽所有來自 /callback 的 Post Request
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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	print('source = ', str(event.source))
	f, cmd_list = xun_op.cmd_parser(event.message.text)
	if f:
		paraList = {}
		paraList['line_bot_api'] = line_bot_api
		paraList['cmd_list'] = cmd_list
		paraList['event'] = event
		paraList['xun_ptt_notify'] = xun_ptt_notify
		f(paraList)

@app.route('/')
def index():
	return render_template('index.html')

# 定時 trigger 自己
@sched.scheduled_job('cron', minute='*/10')
def scheduled_job():
	url = os.environ['LINE_BOT_INDEX_URL']
	conn = rq.urlopen(url)
	
	for key, value in conn.getheaders():
		print(key, value)

sched.start()

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
