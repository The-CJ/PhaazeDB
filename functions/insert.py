import asyncio, json

async def insert(self, request, _INFO):
	""" Used to insert a new entry into a existing container """

	#get required vars (POST -> JSON based)

	#get table_name
	table_name = _INFO.get('_POST', {}).get('into', "")
	if table_name == "":
		table_name = _INFO.get('_JSON', {}).get('into', "")

	if type(table_name) is not str:
		table_name = str(table_name)

	table_name = table_name.replace('..', '')
	table_name = table_name.strip('/')

	#no tabel name
	if table_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'into' field"
		)
		return self.response(status=400, body=json.dumps(res))

	#get content
	content = _INFO.get('_POST', {}).get('content', None)
	if content == None:
		content = _INFO.get('_JSON', {}).get('content', None)

	if type(content) is not dict:
		content = None

	#no content
	if content == None:
		res = dict(
			code=400,
			status="error",
			msg="missing 'content' field as valid json-object"
		)
		return self.response(status=400, body=json.dumps(res))

	#unnamed key
	if content.get('', dummy) != dummy:
		res = dict(
			code=400,
			status="error",
			msg="field 'content' has a unnamed json-object key"
		)
		return self.response(status=400, body=json.dumps(res))

	#get current container from db
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

	# # #

	#get current_id
	_id_ = container['current_id']

	#add entry
	container['data'][_id_] = content
	content['id'] = _id_

	#increase id
	container['current_id'] = _id_ + 1

	# # #

	#save everything
	finished = await self.store(table_name, container)

	if finished:
		res = dict(
			code=201,
			status="inserted",
			msg=f"successfully inserted into container '{table_name}'",
			data=content
		)
		if self.log != False:
			self.logger.info(f"insert entry into '{table_name}': {str(content)}")
		return self.response(status=201, body=json.dumps(res))

	else:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not save your data."
		)
		if self.log != False:
			self.logger.critical(f"insert entry into '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))

class dummy(object):
	pass