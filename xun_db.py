import os
import psycopg2

class xun_db:
	def __init__(self):
		self.database = os.environ['POSTGRES_DATABASE']
		self.user = os.environ['POSTGRES_USER']
		self.password = os.environ['POSTGRES_PASSWORD']
		self.host = os.environ['POSTGRES_HOST']
		self.port = os.environ['POSTGRES_PORT']
		self.table = ['ptt_notify']
	
	def exec_cmd(self, cmd):
		conn = psycopg2.connect(database=self.database,user=self.user,password=self.password,host=self.host,port=self.port)
		cursor = conn.cursor()
		cursor.execute(cmd)
		conn.commit()
		conn.close()
	
	def init_table(self):
		cmd = ''
		for name in self.table:
			cmd += 'CREATE TABLE IF NOT EXISTS %s (date TEXT,job TEXT);' % (name)
		self.exec_cmd(cmd)