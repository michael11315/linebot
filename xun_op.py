import sys
import os
import time
import traceback
import pygsheets
from linebot.models import *
from tool import TracebackLoggingThread

op_cmd = {
	'記帳': 'record',
	'提醒': 'remind',
	# 'ID': 'getid',
	'照片': 'picture',
	'幫助': 'help',
	'測試照片': 'test_picture',
}
op_help_list = ['record', 'remind']
op_help = {
	'record': [
		'記帳指令:',
		'　勳寶 記帳 <花費> <內容> <日期>',
		'　ex: 勳寶 記帳 90 便當 2021/12/06'
		],
	'remind': [
		'提醒指令:',
		'　勳寶 提醒 <數字><秒/分鐘/小時> <內容>',
		'　勳寶 提醒 <年/月/日> <時:分:秒> <內容>',
		'　勳寶 提醒 <時:分:秒> <內容>',
		'　ex: 勳寶 提醒 10分鐘 洗澡',
		'　ex: 勳寶 提醒 2021/11/11 11:11:11 超級雙11',
		'　ex: 勳寶 提醒 23:00:00 睡覺',
		],
}
title_id_map = {
	os.environ['LINE_USER_ID_YO']: '梓佑',
	os.environ['LINE_USER_ID_YEN']: '羽嫣',
	os.environ['LINE_USER_ID_XUAN']: '羽軒',
	}

def cmd_parser(cmd):
	f = None
	cmd_list = cmd.strip().split()
	if cmd_list[0] == '勳寶':
		try:
			if cmd_list[1] in op_cmd:
				f = getattr(sys.modules[__name__], 'func_' + op_cmd[cmd_list[1]])
			else:
				f = func_unknown
		except:
			f = func_unknown
	
	return f, cmd_list

def func_record(paraList):
	def date_format(s):
		try:
			with_year = True
			if s.count('/') == 1:
				with_year = False
			elif s.count('/') != 2:
				raise
			
			date = s.split('/')
			if with_year:
				y = int(date[0])
				if y < 2020 or y > 2030:
					raise
			else:
				y = int(time.strftime('%Y', time.localtime()))
			
			m = int(date[-2])
			if m < 1 or m > 12:
				raise
			
			d = int(date[-1])
			if d < 1 or d > 31:
				raise
			
			return True, '%d/%d/%d' % (y, m, d)
		except:
			#print (traceback.format_exc())
			return False, time.strftime('%Y/%m/%d', time.localtime())
	
	try:
		return_msg = ''
		line_bot_api = paraList['line_bot_api']
		cmd_list = paraList['cmd_list']
		event = paraList['event']
		
		if len(cmd_list) == 2:
			return_msg += '\n'.join(op_help['record'])
		else:
			# update excel
			gc = pygsheets.authorize(service_account_env_var='GC_EXCEL_JSON', seconds_per_quota=5)
			sht = gc.open_by_key('1GASKfCO0WWj_hvyHHfiIlyj4PowaLjWhr9k2vX9EYjM')
			title = title_id_map.get(event.source.user_id, 'other')
			wks = sht.worksheet('title', title)
			
			# add a new row
			# wks.add_rows(1)
			# row_index = wks.rows
			wks.insert_rows(2)
			row_index = 3
			
			# date
			cell = wks.cell('A%d' % row_index)
			ret = date_format(cmd_list[-1])
			cell.value = ret[1]
			
			# dollar
			cell = wks.cell('B%d' % row_index)
			if cmd_list[2].endswith('$') or cmd_list[2].endswith('元'):
				cell.value = cmd_list[2][:-1]
			else:
				cell.value = cmd_list[2]
			
			# content
			cell = wks.cell('C%d' % row_index)
			if ret[0]:
				cell.value = ' '.join(cmd_list[3:-1])
			else:
				cell.value = ' '.join(cmd_list[3:])
			
			# sort by date
			wks.sort_range("A3", "C%d" % wks.rows, sortorder='DESCENDING')
			
			return_msg += '勳寶幫你記帳摟\n'
			return_msg += wks.url
	except:
		print (traceback.format_exc())
		return_msg = '勳寶記帳失敗Orz\n'
		return_msg += '\n'.join(op_help['record'])
	
	message = TextSendMessage(text=return_msg)
	line_bot_api.reply_message(event.reply_token, message)

def func_remind(paraList):
	try:
		return_msg = ''
		line_bot_api = paraList['line_bot_api']
		cmd_list = paraList['cmd_list']
		event = paraList['event']
		
		type, msg, thd = _remind(cmd_list, line_bot_api, event)
		if type == 1:
			pass
		elif type == 2:
			pass
		else:
			raise
		
		return_msg = msg
	except:
		print (traceback.format_exc())
		return_msg = '勳寶提醒失敗Orz\n'
		return_msg += '\n'.join(op_help['remind'])
	
	message = TextSendMessage(text=return_msg)
	line_bot_api.reply_message(event.reply_token, message)
	if thd:
		thd.start()

def func_getid(paraList):
	try:
		return_msg = ''
		line_bot_api = paraList['line_bot_api']
		cmd_list = paraList['cmd_list']
		event = paraList['event']
		
		return_msg += '你的 userId 為: '
		return_msg += event.source.user_id
	except:
		print (traceback.format_exc())
		return_msg = '勳寶拿ID失敗Orz'
	
	message = TextSendMessage(text=return_msg)
	line_bot_api.reply_message(event.reply_token, message)

def func_picture(paraList):
	line_bot_api = paraList['line_bot_api']
	event = paraList['event']
	url = 'https://lh3.googleusercontent.com/pw/AM-JKLXPomWdRHk4fxt5KWQzOlUfpRixNi4m4rDOK0so0XQsuK6gRTNFuQELYO_9wtTcoe2T1F8Jgcw4nfLDrxsmXt2EhQpg84Y-v3WEUuzi3kmh_WZ5hjzu3DRqFmoBD9X4Dy7uIn80vnkLvTlRuhRXTbpO=w613-h817-no'
	image_message = ImageSendMessage(
		original_content_url=url,
		preview_image_url=url
	)
	line_bot_api.reply_message(event.reply_token, image_message)

def func_test_picture(paraList):
	line_bot_api = paraList['line_bot_api']
	cmd_list = paraList['cmd_list']
	event = paraList['event']
	url = cmd_list[2]
	image_message = ImageSendMessage(
		original_content_url=url,
		preview_image_url=url
	)
	line_bot_api.reply_message(event.reply_token, image_message)

def func_help(paraList):
	line_bot_api = paraList['line_bot_api']
	event = paraList['event']
	return_msg = '<勳寶小幫手>\n'
	index = 1
	first_op = True
	for op in op_help_list:
		if first_op:
			first_op = False
		else:
			return_msg += '\n'
		
		return_msg += '%d. ' % (index)
		return_msg += '\n'.join(op_help[op])
		index += 1
	
	message = TextSendMessage(text=return_msg)
	line_bot_api.reply_message(event.reply_token, message)

def func_unknown(paraList):
	line_bot_api = paraList['line_bot_api']
	event = paraList['event']
	return_msg = '勳寶不知道你在說什麼\n'
	return_msg += '(輸入 "勳寶 幫助" 跳出指令介紹)'
	
	message = TextSendMessage(text=return_msg)
	line_bot_api.reply_message(event.reply_token, message)

def _remind(cmd_list, line_bot_api, event):
	try:
		if '/' in cmd_list[2] and ':' in cmd_list[3] or ':' in cmd_list[2]:
			if '/' in cmd_list[2] and ':' in cmd_list[3]:
				ymdhms_str = '%s %s' % (cmd_list[2], cmd_list[3])
				r_msg = ' '.join(cmd_list[4:])
			else: # ':' in cmd_list[2]
				ymd_str = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()).split()[0]
				ymdhms_str = '%s %s' % (ymd_str, cmd_list[2])
				r_msg = ' '.join(cmd_list[3:])
			
			type = 2
			msg = '勳寶會在%s時，提醒你' % (ymdhms_str)
			trigger_time = time.mktime(time.strptime(ymdhms_str, '%Y/%m/%d %H:%M:%S'))
			remind_msg = '記得"%s"喔' % (r_msg)
			thd = TracebackLoggingThread(target=_reminde_thd, args=(trigger_time, line_bot_api, event, remind_msg))
		else:
			now = time.time()
			n = ''
			for s in cmd_list[2]:
				if s in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
					n += s
				else:
					break
			
			unit = cmd_list[2][cmd_list[2].find(n)+len(n):]
			print ('unit:', unit, 'len:', len(unit))
			print ('n:', n)
			n = int(n)
			if unit in ['秒', '秒鐘']:
				pass
			elif unit == ['分', '分鐘']:
				n *= 60
			elif unit == '小時':
				n *= 3600
			else:
				raise
			
			type = 1
			msg = '勳寶會在%s後，提醒你' % (cmd_list[2])
			trigger_time = now + n
			remind_msg = '記得"%s"喔' % (' '.join(cmd_list[3:]))
			thd = TracebackLoggingThread(target=_reminde_thd, args=(trigger_time, line_bot_api, event, remind_msg))
	except:
		type = 0
		msg = ''
		thd = None
		print (traceback.format_exc())
	finally:
		return type, msg, thd

def _reminde_thd(trigger_time, line_bot_api, event, remind_msg):
	try:
		while True:
			time.sleep(1)
			if time.time() > trigger_time:
				break
		
		line_bot_api.push_message(event.source.sender_id, TextSendMessage(text=remind_msg))
	except:
		print (traceback.format_exc())
		line_bot_api.push_message(event.source.sender_id, TextSendMessage(text='勳寶提醒怪怪的'))