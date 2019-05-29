import json, math
from utils.security import password

from aiohttp import web

class Database(object):
	"""Main instance for processing of all database requests"""
	def __init__(self, server):
		self.Server = server
		self.container_root = "DATABASE/"
		self.keep_alive = 60
		self.active = True
		self.save_interval = 0
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
	from functions.storeImport import storeImport
	from functions.storeExport import storeExport

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

		if type(root) is not str:
			self.container_root = "DATABASE/"
			return False

		if not root.endswith("/"):
			root += "/"

		self.container_root = root

		self.Server.Logger.info(f"[Settings] DB root set to: {self.container_root}")
		return True

	def setAliveTime(self, time):
		if type(time) is str:
			if time.isdigit():
				self.keep_alive = int(time)
		elif type(time) is int:
			self.keep_alive = time
		else:
			return False

		self.Server.Logger.info(f"[Settings] DB alive time set to: {self.keep_alive}")
		return True

	def setSaveInterval(self, time):
		if type(time) is str:
			if time.isdigit():
				self.save_interval = int(time)
		elif type(time) is int:
			self.save_interval = time

		else:
			return False

		if self.save_interval < 0:
			self.save_interval = math.inf

		self.Server.Logger.info(f"[Settings] Save interval set to: {self.save_interval}")
		return True

	def sendBackResponse(self, **kwargs):
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeDB v{self.Server.version}"

		if kwargs['headers'].get('Content-Type', None) == None:
			kwargs['headers']['Content-Type'] ="Application/json"

		return web.Response(**kwargs)

	async def storeAllContainer(self, remove_from_ram=True):
		all_success = True
		for container_name in list(self.db):
			if remove_from_ram:
				saved = await self.db[container_name].remove()
			else:
				saved = await self.db[container_name].save()
			if not saved:
				all_success = False
				self.Server.Logger.critical(f"[Save-All] Could not save container: {container_name}")

		return all_success

	async def stop(self):
		# stop all incomming requests
		self.active = False

		# save current containers
		await self.storeAllContainer()

	@web.middleware
	async def mainHandler(self, request, handler):

		# db is about to shutdown
		if not self.active:
			return self.response(status=400, body=json.dumps(dict( code=400, status="rejected", msg="DB is marked as disabled")))

		# is limited to certain ip's
		if self.Server.allowed_ips != []:
			if request.remote not in self.Server.allowed_ips:
				return self.response(status=400, body=json.dumps(dict( code=400, status="rejected",	msg="ip not allowed" )))

		# get process method, default is json
		request.db_method = await self.getMethod(request)

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

	async def getMethod(self, request):
		# change process method, default is json
		# method type must be in a non body part
		method = request.headers.get("X-DB-Method", "").lower()
		if method: return method

		method = request.query.get("X-DB-Method", "").lower()
		if method: return method

		return 'json'

	async def getContent(self, request):
		print(request.db_method)
		# get usable content from Method
		if request.db_method == "json":
			return await self.jsonContent(request)

		else:
			return None

	async def authorise(self, request):
		token = request.db_request.get("token", None)
		if token:
			token = password(token)

		db_token = self.Server.token
		if not db_token: return True

		if token != db_token:
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
			return await self.delete(request)

		elif action == "create":
			return await self.create(request)

		elif action == "drop":
			return await self.drop(request)

		elif action == "show":
			return await self.show(request)

		elif action == "default":
			return await self.default(request)

		elif action == "describe":
			return await self.describe(request)

		elif action == "option":
			return await self.option(request)

		elif action == "import":
			return await self.storeImport(request)

		elif action == "export":
			return await self.storeExport(request)

		else:
			return await self.unknownFunction()

		# # #
