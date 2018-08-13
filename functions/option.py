import asyncio, json, logging

async def option(self, request, _INFO):
	""" Used to change options of the fly """

	#get required vars (POST -> JSON based)

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
			self.log = logging.getLogger('PhaazeDB')
			self.log.setLevel(logging.DEBUG)
			SH = logging.StreamHandler()
			SHF = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
			SH.setFormatter(SHF)
			self.log.addHandler(SH)
		elif v == False:
			self.log = False

		vv = "active" if v == True else "disabled"

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

