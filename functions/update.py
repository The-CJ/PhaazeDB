import asyncio, json, math

async def update(self, request, _INFO):
	""" Used to update entry fields in a existing container """

	#get required vars (POST -> JSON based)

	#get table_name
	table_name = _INFO.get('_POST', {}).get('of', "")
	if table_name == "":
		table_name = _INFO.get('_JSON', {}).get('of', "")

	if type(table_name) is not str:
		table_name = str(table_name)

	table_name = table_name.replace('..', '')
	table_name = table_name.strip('/')

	#no tabel name
	if table_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'of' field"
		)
		return self.response(status=400, body=json.dumps(res))

	#get content
	content = _INFO.get('_POST', {}).get('content', None)
	if content == None:
		content = _INFO.get('_JSON', {}).get('content', None)

	METHOD = None

	if type(content) is dict:
		METHOD = "dict"

	elif type(content) is str:
		METHOD = "str"

	else:
		content = None

	#no content
	if content == None:
		res = dict(
			code=400,
			status="error",
			msg="missing 'content' field as valid json-object or exec() string"
		)
		return self.response(status=400, body=json.dumps(res))

	if METHOD == "dict":
		#unnamed dict key
		if content.get('', dummy) != dummy:
			res = dict(
				code=400,
				status="error",
				msg="field 'content' has a unnamed json-object key"
			)
			return self.response(status=400, body=json.dumps(res))

	#get where :: eval str
	where = _INFO.get('_JSON', {}).get('where', None)
	if where == None:
		where = _INFO.get('_POST', {}).get('where', None)

	if type(where) is not str:
		where = None

	#get offset :: int
	offset = _INFO.get('_GET', {}).get('offset', None)
	if offset == None:
		offset = _INFO.get('_JSON', {}).get('offset', None)
	if offset == None:
		offset = _INFO.get('_POST', {}).get('offset', None)

	if type(offset) is str:
		if offset.isdigit():
			offset = int(offset)
	if type(offset) is not int:
		offset = 0

	#get limit :: int
	limit = _INFO.get('_GET', {}).get('limit', None)
	if limit == None:
		limit = _INFO.get('_JSON', {}).get('limit', None)
	if limit == None:
		limit = _INFO.get('_POST', {}).get('limit', None)

	if type(limit) is str:
		if limit.isdigit():
			limit = int(limit)
	if type(limit) is not int:
		limit = math.inf

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

	#search all entrys
	hits = 0
	found = 0

	for data_id in container.get('data', []):
		data = container['data'][data_id]
		data['id'] = data_id

		if not await check_where(data, where):
			continue

		found += 1
		if offset >= found:
			continue

		if METHOD == "dict":
			for new_data_key in content:
				data[new_data_key] = content[new_data_key]

		elif METHOD == "str":
			try:
				exec(content)
			except Exception as e:
				res = dict(
					code=400,
					status="error",
					msg=f"the exec() string in 'content' has trow a exception"
				)
				return self.response(status=400, body=json.dumps(res))

		hits += 1

		if hits >= limit:
			break

	#save everything
	finished = await self.store(table_name, container)

	if finished:
		res = dict(
			code=201,
			status="updated",
			hits=hits,
			total=len( container.get('data', []) ),
		)
		if self.log != False:
			self.logger.info(f"updated {str(hits)} entry(s) in '{table_name}'")
		return self.response(status=201, body=json.dumps(res))

	else:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not save your data."
		)
		if self.log != False:
				self.logger.critical(f"update entry(s) from '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))

async def check_where(data, where):
	if where == "" or where == None:
		return True

	try:
		if eval(where):
			return True
		else:
			return False
	except:
		return False

class dummy():
	pass
