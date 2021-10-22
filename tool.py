import threading
import traceback

class TracebackLoggingThread(threading.Thread):
	def run(self):
		try:
			super(TracebackLoggingThread, self).run()
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception:
			print ('Uncaught exception in Thread %s' % traceback.format_exc())
			raise