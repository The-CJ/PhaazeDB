import json
import sys

async def storeImport(self, request):
	"""
		Used to import data from file. file extention should be .phzdb
		but can be every type in therory
	"""
	content = await request.post()
	db_file = content.get("phzdb", None)
	print(db_file)

	# prepare request for a valid search
	try:
		# update_request = UpdateRequest(request.db_request)
		return await performImport(self, None)

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performImport(db_instance, request):
	pass
