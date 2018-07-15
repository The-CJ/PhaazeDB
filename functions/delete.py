import asyncio, json, math

async def delete(self, request, _INFO):
	""" Used to delete entrys from the database """

	#get required vars (POST -> JSON based)

	#get tabel name
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

	#get where :: eval str
	where = _INFO.get('_JSON', {}).get('where', None)
	if where == None:
		where = _INFO.get('_POST', {}).get('where', None)

	if type(where) is not str:
		where = None

	#get offset :: int
	offset = _INFO.get('_JSON', {}).get('offset', None)
	if offset == None:
		offset = _INFO.get('_POST', {}).get('offset', None)

	if type(offset) is str:
		if offset.isdigit():
			offset = int(offset)
	if type(offset) is not int:
		offset = 0

	#get limit :: int
	limit = _INFO.get('_JSON', {}).get('limit', None)
	if limit == None:
		limit = _INFO.get('_POST', {}).get('limit', None)

	if type(limit) is str:
		if limit.isdigit():
			limit = int(limit)
	if type(limit) is not int:
		limit = math.inf

	#search all entrys
	hits = 0
	hits_field = 0
	found = 0

	check_list = [_id_ for _id_ in container.get('data', [])]

	for entry_id in check_list:
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		if not await check_where(entry, where):
			continue

		found += 1
		if offset >= found:
			continue

		del container['data'][entry_id]
		hits += 1

		if hits >= limit:
			break

	#save everything
	finished = await self.store(table_name, container)

	if finished:
		res = dict(
			code=201,
			status="deleted",
			hits=hits,
			total=len( container.get('data', []) ),
		)
		return self.response(status=201, body=json.dumps(res))

	else:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not save your data."
		)
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
