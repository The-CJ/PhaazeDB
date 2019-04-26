import json, math

from utils.load import load as load

class MissingOfField(Exception):
	status = 400
class MissingStoreInJoin(Exception):
	status = 400
class InvalidJoin(Exception):
	status = 400
class SysLoadError(Exception):
	status = 500
class ContainerNotFound(Exception):
	status = 404

class SelectRequest(object):
	""" Contains informations for a valid select request,
		does not mean the container exists or where statement has right syntax """
	def __init__(self, db_req):
		self.container:str = None
		self.where:str = ""
		self.fields:list = []
		self.offset:int = -1
		self.limit:int = -1
		self.store:str = None
		self.join:list[dict] = []

		self.getContainter(db_req)
		self.getWhere(db_req)
		self.getFields(db_req)
		self.getOffset(db_req)
		self.getLimit(db_req)
		self.getStore(db_req)
		self.getJoin(db_req)

	def getContainter(self, db_req):
		self.container = db_req.get("of", None)
		if not self.container: raise MissingOfField

	def getWhere(self, db_req):
		self.where = db_req.get("where", "")

	def getFields(self, db_req):
		self.fields = db_req.get("fields", None)
		if type(self.fields) is str:
			self.fields = self.fields.split(",")
		if type(self.fields) is not list:
			self.fields = []

	def getOffset(self, db_req):
		self.offset = db_req.get("offset", -1)
		if type(self.offset) is str:
			if self.offset.isdigit():
				self.offset = int(self.offset)

		if type(self.offset) is not int:
			self.offset = -1

	def getLimit(self, db_req):
		self.limit = db_req.get("limit", -1)
		if type(self.limit) is str:
			if self.limit.isdigit():
				self.limit = int(self.limit)

		if type(self.limit) is not int:
			self.limit = -1

	def getStore(self, db_req):
		self.store = db_req.get("store", None)
		if type(self.store) is not str:
			self.store = None

	def getJoin(self, db_req):
		self.join = db_req.get("join", None)
		if type(self.join) is str:
			try:
				self.join = json.loads(self.join)
			except:
				raise InvalidJoin

async def select(self, request):
	""" Used to select data from ad DB container and give it back, may also include joins to other tables """

	# prepare request for a valid search
	try:
		select_request = SelectRequest(request.db_request)
		return await performSelect(self, select_request)

	except MissingOfField:
		res = dict(
			code=400,
			status="error",
			msg="missing 'of' field"
		)
		return self.response(status=400, body=json.dumps(res))

	except MissingStoreInJoin:
		res = dict(
			code=400,
			status="error",
			msg="missing 'store' field in join"
		)
		return self.response(status=400, body=json.dumps(res))

	except ContainerNotFound:
		res = dict(
			code=404,
			status="error",
			msg=f"container '{select_request.container}' not found"
		)
		return self.response(status=404, body=json.dumps(res))

	except SysLoadError:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not load container file."
		)
		return self.response(status=500, body=json.dumps(res))

async def performSelect(db_instance, select_request):

	result, hits, hits_field, total = await getDataFromContainer(db_instance, select_request)

	#TODO finish select

	#if type(join) != list: join = [join]
	#for j in join:
	#	if j == None: continue
	#	result = await perform_join(self, last_result=result, join=j, parent_name=store)

	res = dict(
		code=200,
		status="selected",

		hits=hits,
		hits_field=hits_field,
		total=total,
		data=result
	)
	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"selected {str(hits)} entry(s) from '{select_request.container}'")
	return db_instance.response(status=200, body=json.dumps(res))

async def getDataFromContainer(db_instance, select_request):
	if select_request.container in [None, ""]: return [], 0, 0, 0

	container = await db_instance.load(select_request.container)

	if container.status == "sys_error": raise SysLoadError
	elif container.status == "not_found": raise ContainerNotFound
	elif container.status == "success":	container = container.content

	# return values
	result = []
	hits = 0
	hits_field = 0


	#go through all entrys
	found = 0
	for entry_id in container.get('data', []):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		# where dont hit entry, means skip, we dont need it
		if not await checkWhere(where=select_request.where, check_entry=entry, check_name=select_request.store):
			continue

		found += 1
		if select_request.offset >= found:
			continue

		requested_fields = await getFields(entry, select_request.fields)

		hits += 1
		hits_field += len(requested_fields)

		result.append( dict(sorted(requested_fields.items())) )

		if hits >= select_request.limit:
			break

	return result, hits, hits_field, len(container.get('data', []) )

async def checkWhere(where="", parent_entry=None, parent_name=None, check_entry=None, check_name=None):

	if not where:
		return True

	if not check_name:
		check_name = "data"

	loc = locals()

	loc[check_name] = check_entry
	loc[parent_name] = parent_entry

	try:
		if eval(where):
			return True
		else:
			return False
	except:
		return False

async def getFields(data, fields):
	if not fields: return data

	requested_fields = dict()
	for field in fields:
		requested_fields[field] = data.get(field, None)

	return requested_fields

async def perform_join(Main_instance, last_result=[], join=dict(), parent_name=None):

	# table_name :: str
	table_name = str(join.get("of", "")).replace('..', '').strip('/')

	# where :: str
	where = join.get("where", None)
	if type(where) is not str:
		where = None

	# fields :: str || list
	fields = join.get("fields", None)
	if type(fields) is str:
		fields = fields.split(',')
	if type(fields) is not list:
		fields = None

	# store :: str
	store = join.get("store", None)

	# include :: bool
	include = bool(join.get("include", False))

	# join :: dict
	join = join.get("join", None)
	if type(join) == str:
		try:
			join = json.loads(join)
		except:
			join = None

	# # #

	if table_name == "": raise MissingOfField

	if store in ["", None]: raise MissingStoreInJoin

	# # #

	container = await Main_instance.load(table_name)

	if container.status == "sys_error": raise SysLoadError
	elif container.status == "not_found": raise ContainerNotFound
	elif container.status == "success":	container = container.content

	for already_selected in last_result:

		result = []

		for entry_id in container.get('data', []):
			entry = container['data'][entry_id]
			entry['id'] = entry_id

			if not await check_where(where_str=where, base_entry=already_selected, base_name=parent_name, check_entry=entry, check_name=store):
				continue

			requested_fields = await check_fields(entry, fields)

			result.append( requested_fields )

		# join entry?
		if type(join) != list: join = [join]
		for j in join:
			if j == None: continue
			result = await perform_join(Main_instance, last_result=result, join=j, parent_name=store)

		if include and len(result) >= 1:
			for field_of_join in result[0]:
				if field_of_join == "id": continue
				already_selected[field_of_join] = result[0][field_of_join]
		else:
			already_selected[store] = result

	return last_result
