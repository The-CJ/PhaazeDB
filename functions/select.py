import json, math

from utils.load import load as load

class MissingOfField(Exception): pass
class SysLoadError(Exception): pass
class ContainerNotFound(Exception): pass

async def select(self, request, _INFO):
	""" Used to select data from ad DB container and give it back """
	#get required vars (GET -> JSON -> POST based)

	# table_name :: str
	table_name = str(get_value(_INFO, "of", "")).replace('..', '').strip('/')

	# where :: str
	where = get_value(_INFO, "where", None)
	if type(where) is not str:
		where = None

	# fields :: str || list
	fields = get_value(_INFO, "fields", None)
	if type(fields) is str:
		fields = fields.split(',')
	if type(fields) is not list:
		fields = None

	# offset :: int
	offset = get_value(_INFO, "offset", 0)
	if type(offset) is str:
		if offset.isdigit():
			offset = int(offset)
	if type(offset) is not int:
		offset = 0

	# limit :: int
	limit = get_value(_INFO, "limit", math.inf)
	if type(limit) is str:
		if limit.isdigit():
			limit = int(limit)
	if type(limit) is not int:
		limit = math.inf
	if limit == 0: limit = 1

	# store :: str
	store = get_value(_INFO, "store", None)

	# join :: dict
	join = get_value(_INFO, "join", None)

	# # #

	try:
		if table_name == "": raise MissingOfField

		container = await self.load(table_name)

		if container.status == "sys_error": raise SysLoadError
		elif container.status == "not_found": raise ContainerNotFound
		elif container.status == "success":	container = container.content

		result, hits, hits_field = await get_data_from_container(container=container, limit=limit, offset=offset, where=where, fields=fields, store=store)

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

	except MissingOfField:
		res = dict(
			code=400,
			status="error",
			msg="missing 'of' field"
		)
		return self.response(status=400, body=json.dumps(res))

	except SysLoadError:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not load container file."
		)
		return self.response(status=500, body=json.dumps(res))

	except ContainerNotFound:
		res = dict(
			code=404,
			status="error",
			msg=f"container '{table_name}' not found"
		)
		return self.response(status=404, body=json.dumps(res))

async def get_data_from_container(container=None, limit=math.inf, offset=0, where=None, fields=[], store=None):
	if container == None: return [], 0, 0

	result = []
	found = 0
	hits = 0
	hits_field = 0

	#go through all entrys
	for entry_id in container.get('data', []):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		if not await check_where(entry, where, store):
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

	return result, hits, hits_field

def get_value(info, value, default):
	v = info.get('_GET', {}).get(value, None)
	if v == None:
		v = info.get('_JSON', {}).get(value, None)
	if v == None:
		v = info.get('_POST', {}).get(value, None)

	if v == None: return default
	else: return v

async def check_where(data, where, store):
	if where == "" or where == None:
		return True

	store if store != None else "data"

	locals()[store] = data

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

