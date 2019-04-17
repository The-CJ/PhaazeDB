import asyncio, logging
from aiohttp import web
import json, time, os, threading, sys, re
try:
	from systemd.journal import JournalHandler
except ImportError:
	pass

SERVER = None
option_re = re.compile(r'^--(.+?)=(.*)$')
all_args = dict()
for arg in sys.argv[1:]:
	d = option_re.match(arg)
	if d != None:
		all_args[d.group(1)] = d.group(2)

class DATABASE(object):
	def __init__(self, config=dict()):
		self.config = config
		self.log = config.get('logging', False)
		self.logger = logging.getLogger('PhaazeDB')
		self.version = "2.0"
		self.active = True
		self.db = dict()
		self.response = self.send_back_response
		if self.logger != False:
			self.logger.setLevel(logging.DEBUG)
			SHF = logging.Formatter("[%(levelname)s]: %(message)s")
			if all_args.get('logging', 'console') == "systemd" and 'systemd' in sys.modules:
				JH = JournalHandler()
				JH.setFormatter(SHF)
				self.logger.addHandler(JH)
			else:
				SH = logging.StreamHandler()
				SH.setFormatter(SHF)
				self.logger.addHandler(SH)

	#functions
	from functions.create import create as create
	from functions.delete import delete as delete
	from functions.drop import drop as drop
	from functions.update import update as update
	from functions.insert import insert as insert
	from functions.select import select as select
	from functions.option import option as option
	from functions.show import show as show
	from functions.describe import describe
	from functions.default import default
	# TODO: add functions.config : to edit configs on the fly without restart

	#website interface
	from admin.interface import web_interface as web_interface

	#errors
	from utils.errors import unauthorised as unauthorised
	from utils.errors import unknown_function as unknown_function
	from utils.errors import missing_function as missing_function

	from utils.load import load
	from utils.store import store

	def send_back_response(self, **kwargs):
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeDB v{self.version}"

		if kwargs['headers'].get('Content-Type', None) == None:
			kwargs['headers']['Content-Type'] ="Application/json"

		return web.Response(**kwargs)

	async def shutdown(self):
		global SERVER

		self.logger.info(f"Preparing shutdown -> 3sec")
		await asyncio.sleep(3)
		await SERVER.shutdown()
		await SERVER.cleanup()
		self.logger.info(f"Shutdown finished")
		exit(1)

	#accessable via web - /admin
	async def interface(self, request):
		if not self.active:
			res = dict(
				code=400,
				status="rejected",
				msg="DB is marked as disabled"
			)
			return self.response(status=400, body=json.dumps(res))

		# is limited to certain ip's
		if self.config.get("allowed_ips", []) != []:
			allowed_ips = self.config.get("allowed_ips", [])
			if request.remote not in allowed_ips:
				res = dict(
					code=400,
					status="rejected",
					msg="ip not allowed"
				)
				return self.response(status=400, body=json.dumps(res))

		return await self.web_interface(request)

	#main entry call point
	async def process(self, request):
		if not self.active:
			res = dict(
				code=400,
				status="rejected",
				msg="DB is marked as disabled"
			)
			return self.response(status=400, body=json.dumps(res))

		# is limited to certain ip's
		if self.config.get("allowed_ips", []) != []:
			allowed_ips = self.config.get("allowed_ips", [])
			if request.remote not in allowed_ips:
				res = dict(
					code=400,
					status="rejected",
					msg="ip not allowed"
				)
				return self.response(status=400, body=json.dumps(res))

		#gather everything
		_GET = request.query
		_POST = dict()
		_JSON = dict()
		_HEADER = request.headers

		try:
			_POST = await request.post()
		except Exception as e:
			pass

		try:
			_JSON = await request.json()
		except Exception as e:
			pass

		#get
		token = request.query.get('token', None)

		#post
		if token == None: token = _POST.get('token', None)

		#json str
		if token == None: token = _JSON.get('token', None)

		#header
		if token == None: token = _HEADER.get('token', None)

		# authorisation failed, block
		if token != self.config.get('auth_token', None):
			return await self.unauthorised()

		#get action
		action = _POST.get('action', None)
		if action == None: action = _JSON.get('action', None)
		if action == None: action = _GET.get('action', None)

		_INFO = dict(_GET=_GET, _POST=_POST, _JSON=_JSON, _HEADER=_HEADER)

		# # #

		if action == None:
			return await self.missing_function()

		elif action == "select":
			return await self.select(request, _INFO)

		elif action == "update":
			return await self.update(request, _INFO)

		elif action == "insert":
			return await self.insert(request, _INFO)

		elif action == "delete":
			return await self.delete(request, _INFO)

		elif action == "create":
			return await self.create(request, _INFO)

		elif action == "drop":
			return await self.drop(request, _INFO)

		elif action == "show":
			return await self.show(request, _INFO)

		elif action == "default":
			return await self.default(request, _INFO)

		elif action == "describe":
			return await self.describe(request, _INFO)

		elif action == "option":
			return await self.option(request, _INFO)

		else:
			return await self.unknown_function()

		# # #

def start_server():

	global SERVER

	#gather configs
	try:
		configs = open("config.json", "rb").read()
		configs = json.loads(configs.decode("UTF-8"))
	except:
		print("`config.json` could not be found, or not read -> Using defaults WARNING: No PassToken.")
		configs = dict()

	#check for DATABASE folder
	try:
		f = os.listdir('DATABASE/')
	except:
		os.mkdir('DATABASE')

	#make app
	DB = DATABASE(config=configs)
	SERVER = web.Application()

	#web interface route
	SERVER.router.add_route('GET', '/admin{useless:.*}', DB.interface)
	SERVER.router.add_route("GET", "/favicon.ico", DB.interface)
	#main route
	SERVER.router.add_route('*', '/{useless:.*}', DB.process)

	#start
	DB.logger.info(f"Starting PhaazeDB v{DB.version}")
	DB.logger.info(f"Running on port: {configs.get('port', 3000)}")
	if configs.get("allowed_ips", []) != []:
		ips = configs.get("allowed_ips", [])
		ips_str = ", ".join("["+ip+"]" for ip in ips)
	else:
		ips_str = "--ALL--"
	DB.logger.info(f"Allowed IP's: {ips_str}")
	DB.logger.info(f"Action Logging: {DB.log}")

	web.run_app(SERVER, port=configs.get('port', 3000), print=False)

start_server()
