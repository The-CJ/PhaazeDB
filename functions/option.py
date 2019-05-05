import json
from utils.errors import MissingOptionField

class OptionRequest(object):
	""" Contains informations for a valid option request,
		does not mean the option actully exists or given parameter are possible"""
	def __init__(self, db_req):
		self.option:str = None
		self.value:str = None

	def getOption(self, db_req):
		self.option = db_req.get("option", None)
		if type(self.option) is not str:
			self.option = None

		if not self.option: raise MissingOptionField()

	def getValue(self, db_req):
		self.value = db_req.get("value", None)
		if type(self.value) is not str:
			self.value = None

async def option(self, request):
	""" Used to change options on the fly """

	# prepare request for a valid insert
	try:
		option_request = OptionRequest(request.db_request)
		return await performOption(self, option_request)

	except (MissingOptionField) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performOption(db_instance, option_request):

	if option_request.option == "log":
		return await performLogging(db_instance, option_request)

	elif option_request.option == "shutdown":
		return await performShutdown(db_instance, option_request)

	else:
		raise MissingOptionField(True)

async def performLogging(db_instance, option_request):
	v = None

	# fix value from call
	if option_request.value != None:
		db_instance.Server.action_logging = bool(option_request.value)
	# toggle
	else:
		db_instance.Server.action_logging = False if db_instance.Server.action_logging else True

	vv = "active" if v == True else "disabled"
	db_instance.Server.Logger.info(f"Action logging now: {vv}")

	res = dict(
		code=200,
		status="success",
		msg=f"'action_logging' is now {vv}"
	)
	return db_instance.response(status=200, body=json.dumps(res))

async def performShutdown(db_instance, option_request):
		self.active = False

		asyncio.ensure_future(self.shutdown())

		res = dict(
			code=200,
			status="success",
			msg="DB is sutting down"
		)
		return self.response(status=200, body=json.dumps(res))
