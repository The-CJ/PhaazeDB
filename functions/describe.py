import os, pickle, json
from datetime import datetime

async def describe(self, request, _INFO):
	""" Used to get the defaults value list of a container """

	#get required vars (GET -> JSON -> POST based)

	#get tabel name
	table_name = _INFO.get('_GET', {}).get('name', None)
	if table_name == None:
		table_name = _INFO.get('_JSON', {}).get('name', None)
	if table_name == None:
		table_name = _INFO.get('_POST', {}).get('name', None)

	if table_name == None:
		table_name = ""
	else:
		table_name = str(table_name)

	table_name = table_name.replace('..', '')
	table_name = table_name.strip('/')

	#no tabel name
	if table_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'name' field"
		)
		return self.response(status=400, body=json.dumps(res))

	try:
		#get container
		container = await self.load(table_name)

		#error handling
		if container.status == "sys_error":
			# this SHOULD never happen, but hey... just in case
			res = dict(
				code=500,
				status="error",
				msg="DB could not load container file."
			)
			return self.response(status=500, body=json.dumps(res))

		elif container.status == "not_found":
			res = dict(
				code=404,
				status="error",
				msg=f"container '{table_name}' not found"
			)
			return self.response(status=404, body=json.dumps(res))

		elif container.status == "success":

			container = container.content

		default_template = container.get("default", dict())

		#awnser
		res = dict(
			code=200,
			status="described",
			container=table_name,
			default=default_template,
			msg=f"described container '{table_name}'"
		)
		if self.log != False:
			self.logger.info(f"described container '{table_name}'")
		return self.response(status=200, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		if self.log != False:
			self.logger.critical(f"described container '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))
