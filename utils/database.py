import json

from aiohttp import web

class Database(object):
	"""Main instance for processing of all database requests"""
	def __init__(self, server):
		self.Server = server
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
	from utils.errors import unknown_function as unknown_function
	from utils.errors import missing_function as missing_function

	# utils
	from utils.load import load
	from utils.store import store

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

		request.db_method = request.headers.get("X-DB-Method", "json").lower()


		try:
			# get usable content from Method
			if request.db_method == "json":
				request.db_request = await request.json()

			else:
				return self.response( body=json.dumps(dict(msg="unsupported 'X-DB-Method'", status=405)),	status=405 )

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

		return await self.webInterface(request)

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
