import json, math

from utils.load import load as load

async def select(self, request, _INFO):
	""" Used to select data from ad DB container and give it back """

	#get required vars (GET -> JSON -> POST based)

	#get tabel name
	table_name = _INFO.get('_GET', {}).get('of', "")
	if table_name == "":
		table_name = _INFO.get('_JSON', {}).get('of', "")
	if table_name == "":
		table_name = _INFO.get('_POST', {}).get('of', "")

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

	#get optional vars (GET -> JSON -> POST based)

	#get where :: eval str
	where = _INFO.get('_GET', {}).get('where', None)
	if where == None:
		where = _INFO.get('_JSON', {}).get('where', None)
	if where == None:
		where = _INFO.get('_POST', {}).get('where', None)

	if type(where) is not str:
		where = None

	#get fields :: list || comma string
	fields = _INFO.get('_GET', {}).get('fields', None)
	if fields == None:
		fields = _INFO.get('_JSON', {}).get('fields', None)
	if fields == None:
		fields = _INFO.get('_POST', {}).get('fields', None)

	if type(fields) is str:
		fields = fields.split(',')
	if type(fields) is not list:
		fields = None

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

	#search all entrys
	hits = 0
	hits_field = 0
	found = 0
	result = []

	for entry_id in container.get('data', []):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		if not await check_where(entry, where):
			continue

		found += 1
		if offset >= found:
			continue

		requested_fields = await check_fields(entry, fields)

		hits += 1
		hits_field += len(requested_fields)

		result.append( dict(sorted(requested_fields.items())) )

		if hits >= limit:
			break

	res = dict(
		code=200,
		status="selected",
		hits=hits,
		hits_field=hits_field,
		total=len( container.get('data', []) ),
		data=result
	)
	if self.log != False:
		self.logger.info(f"selected {str(hits)} entry(s) from '{table_name}'")
	return self.response(status=200, body=json.dumps(res))

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

async def check_fields(data, fields):
	if fields == None or fields == []:
		return data

	requested_fields = dict()
	for field in fields:
		requested_fields[field] = data.get(field, None)

	return requested_fields

