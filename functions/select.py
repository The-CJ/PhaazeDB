import json, math

from utils.load import load as load

class MissingOfField(Exception): pass
class MissingStoreInJoin(Exception): pass
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
	if type(store) is not str:
		store = None

	# join :: dict
	join = get_value(_INFO, "join", None)
	if type(join) == str:
		try:
			join = json.loads(join)
		except:
			join = None

	# # #

	try:
		if table_name == "": raise MissingOfField

		result, hits, hits_field, total = await get_data_from_container(
			self,
			container=table_name,
			limit=limit,
			offset=offset,
			where=where,
			fields=fields,
			store=store
		)

		# join entry?
		if type(join) == dict:
			result = await perform_join(self, result, join)

		res = dict(
			code=200,
			status="selected",

			hits=hits,
			hits_field=hits_field,
			total=total,
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

async def get_data_from_container(Main_instance, container=None, limit=math.inf, offset=0, where=None, fields=[], store=None):
	if container == None: return [], 0, 0, 0

	container = await Main_instance.load(container)

	if container.status == "sys_error": raise SysLoadError
	elif container.status == "not_found": raise ContainerNotFound
	elif container.status == "success":	container = container.content

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

	return result, hits, hits_field, len(container.get('data', []) )

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

async def perform_join(Main_instance, current_result, join):

	# table_name :: str
	table_name = str(get_value(join, "of", "")).replace('..', '').strip('/')

	# where :: str
	where = get_value(join, "where", None)
	if type(where) is not str:
		where = None

	# fields :: str || list
	fields = get_value(join, "fields", None)
	if type(fields) is str:
		fields = fields.split(',')
	if type(fields) is not list:
		fields = None

	# store :: str
	store = get_value(join, "store", None)
	if table_name == "": raise MissingStoreInJoin

	# join :: dict
	join = get_value(join, "join", None)
	if type(join) == str:
		try:
			join = json.loads(join)
		except:
			join = None

	# # #

	if table_name == "": raise MissingOfField

	# # #

	container = await Main_instance.load(table_name)

	if container.status == "sys_error": raise SysLoadError
	elif container.status == "not_found": raise ContainerNotFound
	elif container.status == "success":	container = container.content

	for already_selected in current_result:

		result = []

		for entry_id in container.get('data', []):
			entry = container['data'][entry_id]
			entry['id'] = entry_id

			if not await check_where(where_str=where, base_container=already_selected, base_name=None, check_entry=entry, check_name=store):
				continue

			requested_fields = await check_fields(entry, fields)

			result.append( dict(sorted(requested_fields.items())) )

			if hits >= limit:
				break

		return result, hits, hits_field, len(container.get('data', []) )

		# join entry?
		if type(join) == dict:
			result = await perform_join(self, result, join)

		already_selected[store] = result

	return current_result