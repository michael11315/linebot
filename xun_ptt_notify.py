import xun_db
from tool import TracebackLoggingThread

class xun_ptt_notify:
	def __init__(self):
		self.db = xun_db.xun_db()
		self.db.init_table()
		self.load_db()
	
	def load_db(self):
		pass

def xun_ptt_notifyer(xun_ptt_notify):
	while True:
		pass