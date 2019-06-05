from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from phaazedb import PhaazeDBServer

import json
from utils.security import password
from aiohttp.web import Application, middleware, Request, StreamResponse, Response, HTTPException
from utils.loader import DBRequest

class Database(object):
	"""Main instance for processing of all database requests"""
	def __init__(self, PhaazeDBS):
		self.PhaazeDBS:"PhaazeDBServer" = PhaazeDBS
		self.container_root:str = "DATABASE/"
		self.keep_alive:int = 60
		self.active:bool = True
		self.save_interval:int = 0

		# main db
		self.db:dict = dict()

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
	from utils.loader import jsonContent, postContent

	def setRoot(self, root:str) -> bool:
		if root == None:
			self.container_root = "DATABASE/"

		if type(root) is not str:
			self.container_root = "DATABASE/"
			return False

		if not root.endswith("/"):
			root += "/"

		self.container_root = root

		self.PhaazeDBS.Logger.info(f"[Settings] DB root set to: {self.container_root}")
		return True

	def setAliveTime(self, time:int) -> bool:
		if type(time) is str:
			if time.isdigit():
				self.keep_alive = int(time)
		elif type(time) is int:
			self.keep_alive = time
		else:
			return False

		self.PhaazeDBS.Logger.info(f"[Settings] DB alive time set to: {self.keep_alive}")
		return True

	def setSaveInterval(self, time:int) -> bool:
		if type(time) is str:
			if time.isdigit():
				self.save_interval = int(time)
		elif type(time) is int:
			self.save_interval = time

		else:
			return False

		self.PhaazeDBS.Logger.info(f"[Settings] Save interval set to: {self.save_interval}")
		return True

	def response(self, **kwargs:Any) -> Response:
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeDB v{self.PhaazeDBS.version}"

		if kwargs['headers'].get('Content-Type', None) == None:
			kwargs['headers']['Content-Type'] ="Application/json"

		return Response(**kwargs)

	async def storeAllContainer(self, remove_from_ram:bool=True) -> bool:
		all_success:bool = True
		for container_name in list(self.db):
			if remove_from_ram:
				saved = await self.db[container_name].remove()
			else:
				saved = await self.db[container_name].save()
			if not saved:
				all_success = False
				self.PhaazeDBS.Logger.critical(f"[Save-All] Could not save container: {container_name}")

		return all_success

	async def stop(self) -> None:
		# stop all incomming requests
		self.active = False

		# save current containers
		await self.storeAllContainer()

	@middleware
	async def mainHandler(self, WebRequest:Request, handler:Callable) -> Response or StreamResponse:
		if WebRequest.match_info.get("x", "") == "import":
			# import files can be giants
			WebRequest._client_max_size = -1

		# db is about to shutdown or its currently importing
		if not self.active:
			return self.response(status=400, body=json.dumps(dict( code=400, status="rejected", msg="DB is marked as disabled")))

		# is limited to certain ip's
		if self.PhaazeDBS.allowed_ips != []:
			if WebRequest.remote not in self.PhaazeDBS.allowed_ips:
				return self.response(status=400, body=json.dumps(dict( code=400, status="rejected",	msg="ip not allowed" )))

		# get process method, default is json
		WebRequest.db_method:str = await self.getMethod(WebRequest)

		try:
			Resp:Response = await handler(WebRequest)
			return Resp

		except HTTPException as Http_ex:
			return self.response(
				body=json.dumps(dict(msg=Http_ex.reason, status=Http_ex.status)),
				status=Http_ex.status
			)

		except Exception as e:
			self.PhaazeDBS.Logger.error(str(e))
			return self.response(status=500)

	async def getMethod(self, WebRequest:Request) -> str:
		# change process method, default is json
		# method type must be in a non body part
		method:str = WebRequest.headers.get("X-DB-Method", "").lower()
		if method: return method

		method = WebRequest.query.get("X-DB-Method", "").lower()
		if method: return method

		return 'json'

	async def getContent(self, WebRequest:Request) -> DBRequest:
		# get usable content from Method
		if WebRequest.db_method == "json":
			return await self.jsonContent(WebRequest)

		if WebRequest.db_method == "post":
			return await self.postContent(WebRequest)

		else:
			return None

	async def authorise(self, DBReq:DBRequest) -> bool:
		token:str = DBReq.get("token", None)
		if token:
			token = password(token)

		db_token:str = self.PhaazeDBS.token
		if not db_token: return True

		if token != db_token:
			return False
		else:
			return True

	#accessable via web - /admin
	async def interface(self, WebRequest:Request) -> Response:
		return await self.webInterface(WebRequest)

	#main entry call point
	async def process(self, WebRequest:Request) -> Response or StreamResponse:

		DBReq:DBRequest = await self.getContent(WebRequest)

		# none supported
		if DBReq == None:
			return self.response( body=json.dumps(dict(msg="unsupported 'X-DB-Method'", status=405)),	status=405 )

		if DBReq.success == False:
			return self.response( body=json.dumps(dict(msg=DBReq.error_msg, status=400)),	status=400 )

		if not await self.authorise(DBReq):
			return await self.unauthorised()

		action:str = DBReq.get("action", None)

		# # #

		if action == None:
			return await self.missingFunction()

		elif action == "select":
			return await self.select(WebRequest, DBReq)

		elif action == "update":
			return await self.update(WebRequest)

		elif action == "insert":
			return await self.insert(WebRequest, DBReq)

		elif action == "delete":
			return await self.delete(WebRequest)

		elif action == "create":
			return await self.create(WebRequest)

		elif action == "drop":
			return await self.drop(WebRequest)

		elif action == "show":
			return await self.show(WebRequest, DBReq)

		elif action == "default":
			return await self.default(WebRequest)

		elif action == "describe":
			return await self.describe(WebRequest)

		elif action == "option":
			return await self.option(WebRequest)

		elif action == "import":
			return await self.storeImport(WebRequest)

		elif action == "export":
			return await self.storeExport(WebRequest)

		else:
			return await self.unknownFunction()
