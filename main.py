import http.server
import json

from functions.create import create as create
from functions.delete import delete as delete
from functions.drop import drop as drop
from functions.update import update as update
from functions.insert import insert as insert
from functions.select import select as select

DUMP = {}

class RequestHandler(http.server.BaseHTTPRequestHandler):

	def do_GET(self):
		self.process()

	def do_POST(self):
		self.process()

	def process(self):
		try: length = int(self.headers["Content-Length"])
		except: length = 0

		content = self.rfile.read(length)

		try:
			content=json.loads(content)
		except:
			content = {}

		db_user = content.get('login', None)
		db_password = content.get('password', None)

		allow = False
		for user in perms.get('auth', []):
			if db_user == user.get('login', None) and db_password == user.get('password', None):
				allow = True

		if allow == False:
			self.send_response(401)
			self.end_headers()
			self.wfile.write(b'{"error":"missing or wrong login data"}')
			self.wfile.flush()
			return

		action = content.get('action', None)
		#get method
		if action == None:
			self.send_response(400)
			self.end_headers()
			self.wfile.write(b'{"error": "missing body"}')
			self.wfile.flush()
			return

		if action.lower() == "create":
			rsp = create(content)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "delete":
			rsp = delete(content)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "drop":
			rsp = drop(content)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "update":
			rsp = update(content)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "insert":
			rsp = insert(content, DUMP)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "select":
			rsp = select(content)

			self.send_response(rsp.response)
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		else:
			self.send_response(406)
			self.end_headers()
			self.wfile.write(b'{"error":"method not supported"}')
			self.wfile.flush()

	#def log_message(self, format, *args):
		#return

def webserver(perms):
	server = http.server.HTTPServer(( perms.get("adress", "0.0.0.0"), perms.get("port", 1001) ), RequestHandler)
	server.serve_forever()

perms = open("config.json", "rb").read()
try:
	perms = json.loads(perms)
except:
	print("Error reading config.json")

webserver(perms)