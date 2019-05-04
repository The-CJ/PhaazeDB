import json

from aiohttp import web

class Database(object):
	"""Main instance for processing of all database requests"""
	def __init__(self, server):
		self.Server = server
		self.container_root = "DATABASE/"
		self.keep_alive = 60
		self.config = self.Server.config #REMOVE THIS
		self.log = self.Server.action_logging #REMOVE THIS
		self.active = True
		self.response = self.sendBackResponse

		# main db
		self.db = dict()

	# functions
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

	# website
	from admin.interface import webInterface as webInterface

	# errors
	from utils.errors import unauthorised as unauthorised
	from utils.errors import unknownFunction as unknownFunction
	from utils.errors import missingFunction as missingFunction
	from utils.errors import criticalError as criticalError

	# utils
	from utils.load import load
	from utils.store import store

	# content load method load-parser
	from utils.loader import jsonContent

	def setRoot(self, root):
		if root == None:
			self.container_root = "DATABASE/"
			return False
		if not root.endswith("/"):
			root += "/"
		self.container_root = root

	def setAliveTime(self, time):
		if type(time) is str:
			if time.isdigit():
				self.keep_alive = int(time)
				return True
		if type(time) is int:
			self.keep_alive = time
			return True
		return False

	def sendBackResponse(self, **kwargs):
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeDB v{self.Server.version}"

		if kwargs['headers'].get('Content-Type', None) == None:
			kwargs['headers']['Content-Type'] ="Application/json"

		return web.Response(**kwargs)

	async def stop(self):
		pass
		# TODO: CLEANUP

	@web.middleware
	async def mainHandler(self, request, handler):

		# db is about to shutdown
		if not self.active:
			return self.response(status=400, body=json.dumps(dict( code=400, status="rejected", msg="DB is marked as disabled")))

		# is limited to certain ip's
		if self.Server.config.get("allowed_ips", []) != []:
			allowed_ips = self.Server.config.get("allowed_ips", [])
			if request.remote not in allowed_ips:
				return self.response(status=400, body=json.dumps(dict( code=400, status="rejected",	msg="ip not allowed" )))

		# get process method, default is json
		request.db_method = request.headers.get("X-DB-Method", "json").lower()

		try:
			response = await handler(request)
			return response

		except web.HTTPException as http_ex:
			return self.response(
				body=json.dumps(dict(msg=http_ex.reason, status=http_ex.status)),
				status=http_ex.status
			)

		except Exception as e:
			self.Server.Logger.error(str(e))
			return self.response(status=500)

	async def getContent(self, request):
		# get usable content from Method
		if request.db_method == "json":
			return await self.jsonContent(request)

		else:
			return None

	async def authorise(self, request):
		token = request.db_request.get("token", None)
		if token != self.Server.config.get('auth_token', None):
			return False
		else:
			return True

	#accessable via web - /admin
	async def interface(self, request):
		return await self.webInterface(request)

	#main entry call point
	async def process(self, request):

		request.db_request = await self.getContent(request)

		# none supported
		if request.db_request == None:
			return self.response( body=json.dumps(dict(msg="unsupported 'X-DB-Method'", status=405)),	status=405 )

		if request.db_request.success == False:
			return self.response( body=json.dumps(dict(msg=request.db_request.error_msg, status=400)),	status=400 )

		if not await self.authorise(request):
			return await self.unauthorised()

		action = request.db_request.get("action", None)

		# # #

		if action == None:
			return await self.missingFunction()

		elif action == "select":
			return await self.select(request)

		elif action == "update":
			return await self.update(request)

		elif action == "insert":
			return await self.insert(request)

		elif action == "delete":
			return await self.delete(request, _INFO)

		elif action == "create":
			return await self.create(request)

		elif action == "drop":
			return await self.drop(request, _INFO)

		elif action == "show":
			return await self.show(request)

		elif action == "default":
			return await self.default(request, _INFO)

		elif action == "describe":
			return await self.describe(request, _INFO)

		elif action == "option":
			return await self.option(request, _INFO)

		else:
			return await self.unknownFunction()

		# # #
