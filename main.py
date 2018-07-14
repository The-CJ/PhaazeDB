import asyncio
from aiohttp import web
import json, time, os, threading


class DATABASE(object):
	def __init__(self, config=dict()):
		self.config = config
		self.version = "2.0"
		self.active = True
		self.db = dict()
		self.response = self.send_back_response

	#functions
	from functions.create import create as create
	from functions.delete import delete as delete
	from functions.drop import drop as drop
	from functions.update import update as update
	from functions.insert import insert as insert
	from functions.select import select as select
	from functions.show import show as show

	#website
	from admin.website import website as website

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
		kwargs['headers']['Content-Type'] ="Application/json"
		return web.Response(**kwargs)

	#accessable via web - /admin
	async def interface(self, request):
		return self.website()

	#main entry call point
	async def process(self, request):
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

		_INFO = dict(_GET=_GET, _POST=_POST, _JSON=_JSON, _HEADER=_HEADER)

		# # #

		if action == None:
			return await self.missing_function()

		elif action == "create":
			return await self.create(request, _INFO)

		elif action == "delete":
			return await self.delete(request, _INFO)

		elif action == "drop":
			return await self.drop(request, _INFO)

		elif action == "insert":
			return await self.insert(request, _INFO)

		elif action == "select":
			return await self.select(request, _INFO)

		elif action == "show":
			pass

		elif action == "update":
			pass

		else:
			return await self.unknown_function()

		# # #

def start_server():

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
	server = web.Application()

	#web interface route
	server.router.add_route('GET', '/admin{useless:.*}', DB.interface)
	#main route
	server.router.add_route('*', '/{useless:.*}', DB.process)

	#start
	try:
		print(open("logo.txt", "r").read())
	except:
		pass
	web.run_app(server, port=configs.get('port', 1001))

start_server()
