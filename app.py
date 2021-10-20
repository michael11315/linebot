import os
from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

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
	if event.message.text == '1':
		url = 'https://lh3.googleusercontent.com/pw/AM-JKLXPomWdRHk4fxt5KWQzOlUfpRixNi4m4rDOK0so0XQsuK6gRTNFuQELYO_9wtTcoe2T1F8Jgcw4nfLDrxsmXt2EhQpg84Y-v3WEUuzi3kmh_WZ5hjzu3DRqFmoBD9X4Dy7uIn80vnkLvTlRuhRXTbpO=w613-h817-no'
		image_message = ImageSendMessage(
			original_content_url=url,
			preview_image_url=url
		)
		line_bot_api.reply_message(event.reply_token, image_message)
	else:
		message = TextSendMessage(text=event.message.text)
		line_bot_api.reply_message(event.reply_token, message)

@app.route('/')
def index():
	return 'Hello World'

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
