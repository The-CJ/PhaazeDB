import json

class OptionRequest(object):
	""" Contains informations for a valid option request,
		does not mean the option actully exists or given parameter are possible"""
	def __init__(self, db_req):
		pass


async def option(self, request):
	""" Used to change options on the fly """

	# prepare request for a valid insert
	try:
		option_request = OptionRequest(request.db_request)
		return await performOption(self, option_request)

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performOption(db_instance, option_request):
	#get table_name
	option = _INFO.get('_POST', {}).get('option', "")
	if option == "":
		option = _INFO.get('_JSON', {}).get('option', "")

	if type(option) is not str:
		option = str(option)

	#no option
	if option == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'option' field"
		)
		return self.response(status=400, body=json.dumps(res))

	#get value
	value = _INFO.get('_POST', {}).get('value', None)
	if value == None:
		value = _INFO.get('_JSON', {}).get('value', None)

	if type(value) is not str:
		value = None

	# # # # #

	if option == "log":

		v = None

		if value.lower() == "true": v = True
		elif value.lower() == "false": v = False

		if v == None:
			if self.log == False: v = True
			else: v = False

		if v == True:
			self.log = True
		elif v == False:
			self.log = False

		vv = "active" if v == True else "disabled"

		self.logger.info(f"Logging Module: '{vv}'")

		res = dict(
			code=200,
			status="success",
			msg="option 'log' is now " + vv
		)
		return self.response(status=200, body=json.dumps(res))

	elif option == "shutdown":
		self.active = False

		asyncio.ensure_future(self.shutdown())

		res = dict(
			code=200,
			status="success",
			msg="DB is sutting down"
		)
		return self.response(status=200, body=json.dumps(res))

