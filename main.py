import http.server
import json, time, os

from functions.create import create as create
from functions.delete import delete as delete
from functions.drop import drop as drop
from functions.update import update as update
from functions.insert import insert as insert
from functions.select import select as select
from functions.show import show as show

from admin.website import website as website

DUMP = {}
CLOSE = False

class RequestHandler(http.server.BaseHTTPRequestHandler):

	log = []

	def do_GET(self):
		self.process()

	def do_POST(self):
		self.process()

	def process(self):
		global CLOSE
		if CLOSE:
			return

		if self.path.startswith('/admin'):
			r = website(self.path)
			self.send_response(200)
			self.end_headers()
			if type(r) is not bytes:
				r = r.encode('UTF-8')

			self.wfile.write(r)
			self.wfile.flush()
			return


		try: length = int(self.headers["Content-Length"])
		except: length = 0

		content = self.rfile.read(length)

		try:
			content = json.loads(content.decode("UTF-8"))
		except:
			content = None

		if content == None:
			self.send_response(400)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(dict(status="error", msg="missing or corrupted content body")).encode("UTF-8"))
			self.wfile.flush()
			return

		token = content.get('token', None)

		allow = False
		if token == perms.get('auth_token', None):
			allow = True

		if allow == False:
			self.send_response(401)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(dict(status="error", msg="unauthorised")).encode("UTF-8"))
			self.wfile.flush()
			return

		action = content.get('action', None)
		#get method
		if action == None:
			self.send_response(400)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(dict(status="error", msg="missing 'action'")).encode("UTF-8"))
			self.wfile.flush()
			return

		if action.lower() == "create":
			rsp = create(content)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "delete":
			rsp = delete(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "drop":
			rsp = drop(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "update":
			rsp = update(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "insert":
			rsp = insert(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "select":
			rsp = select(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "show":
			rsp = show(content, DUMP)

			self.send_response(rsp.response)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(rsp.content)
			self.wfile.flush()

		elif action.lower() == "shutdown":
			CLOSE = True
			time.sleep(5)
			exit(1)

		else:
			self.send_response(406)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(dict(status="error", msg="method '{}' not supported".format(action))).encode("UTF-8"))
			self.wfile.flush()

	def log_message(self, _format, *args):
		return

def webserver(perms):
	server = http.server.HTTPServer(( perms.get("adress", "0.0.0.0"), perms.get("port", 1001) ), RequestHandler)
	server.serve_forever()

try:
	perms = open("config.json", "rb").read()
	perms = json.loads(perms.decode("UTF-8"))
except:
	print("`config.json` could not be found, or not read -> Using defaults WARNING: No PassToken.")
	time.sleep(3)
	perms = {"auth_token": ""}

#check for DATABASE
try:
	f = os.listdir('DATABASE/')
except:
	os.mkdir('DATABASE')

print(open("logo.txt", "r").read())
print("Running on port: "+str(perms.get("port", 1001)) + "\n")

webserver(perms)