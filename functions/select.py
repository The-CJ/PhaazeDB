import json, math, copy
from utils.errors import MissingOfField, MissingStoreInJoin, ContainerNotFound, SysLoadError, InvalidJoin, InvalidLimit

class SelectRequest(object):
	""" Contains informations for a valid select request,
		does not mean the container exists or where statement has right syntax """
	def __init__(self, db_req, is_join=False):
		self.container:str = None
		self.where:str = ""
		self.fields:list = []
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None
		self.join:list[dict] = []
		self.is_join:bool = is_join
		self.include:bool = False

		self.getContainter(db_req)
		self.getWhere(db_req)
		self.getFields(db_req)
		self.getOffset(db_req)
		self.getLimit(db_req)
		self.getStore(db_req)
		self.getJoin(db_req)
		self.getInclude(db_req)

	def getContainter(self, db_req):
		self.container = db_req.get("of", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingOfField()

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
		self.limit = db_req.get("limit", math.inf)
		if type(self.limit) is str:
			if self.limit.isdigit():
				self.limit = int(self.limit)

		if type(self.limit) is not int:
			self.limit = math.inf

		if self.limit <= 0:
			raise InvalidLimit()

	def getStore(self, db_req):
		self.store = db_req.get("store", None)
		if type(self.store) is not str:
			self.store = None

		if not self.store and self.is_join:
			raise MissingStoreInJoin()

	def getJoin(self, db_req):
		self.join = db_req.get("join", None)
		if type(self.join) is str:
			try:
				self.join = json.loads(self.join)
			except:
				raise InvalidJoin()
		if type(self.join) != list: self.join = [self.join]

	def getInclude(self, db_req):
		self.include = bool(db_req.get("include", False))

async def select(self, request):
	""" Used to select data from ad DB container and give it back, may also include joins to other tables """

	# prepare request for a valid search
	try:
		select_request = SelectRequest(request.db_request)
		return await performSelect(self, select_request)

	except MissingStoreInJoin:
		res = dict(
			code=400,
			status="error",
			msg="missing 'store' field in join"
		)
		return self.response(status=400, body=json.dumps(res))

	except (ContainerNotFound, MissingOfField, SysLoadError, InvalidLimit) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performSelect(db_instance, select_request:SelectRequest):

	result, hits, hits_field, total = await getDataFromContainer(db_instance, select_request)

	for join in select_request.join:
		if join == None: continue
		select_join_request = SelectRequest(join, is_join=True)
		result = await performJoin(db_instance, result, select_join_request, parent_name=select_request.store)

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

async def getDataFromContainer(db_instance, select_request:SelectRequest, parent_name:str=None, parent_entry:dict=None):
	if select_request.container in [None, ""]: return [], 0, 0, 0

	container = await db_instance.load(select_request.container)

	if container.status == "sys_error": raise SysLoadError(select_request.container)
	elif container.status == "not_found": raise ContainerNotFound(select_request.container)
	elif container.status == "success":	container = container.content

	# return values
	result = []
	hits = 0
	hits_field = 0

	#go through all entrys
	found = 0
	default_set = container.get("default", {})

	for entry_id in container.get('data', []):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		# where dont hit entry, means skip, we dont need it
		if not await checkWhere(where=select_request.where, parent_name=parent_name, parent_entry=parent_entry, check_entry=entry, check_name=select_request.store):
			continue

		found += 1
		if select_request.offset >= found:
			continue

		# copy entry before further actions, so the entry in the db itself does not get the default set added to permanent memory
		entry = copy.deepcopy(entry)

		# complete entry
		for default_key in default_set:
			if entry.get(default_key, EmptyObject) == EmptyObject:
				entry[default_key] = container["default"][default_key]

		# only gather what the user wants
		requested_fields = await getFields(entry, select_request.fields)

		hits += 1
		hits_field += len(requested_fields)

		result.append( requested_fields )

		if hits >= select_request.limit:
			break

	return result, hits, hits_field, len(container.get('data', []) )

async def checkWhere(where="", parent_entry:dict=None, parent_name:str=None, check_entry:dict=None, check_name:str=None):

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

async def performJoin(db_instance, last_result:list, join_request:SelectRequest, parent_name:str=None):

	container = await db_instance.load(join_request.container)

	if container.status == "sys_error": raise SysLoadError(join_request.container)
	elif container.status == "not_found": raise ContainerNotFound(join_request.container)
	elif container.status == "success":	container = container.content

	# for every already selected entry, take the data and go in the next container
	for already_selected in last_result:

		join_result, *x = await getDataFromContainer(db_instance, join_request, parent_name=parent_name, parent_entry=already_selected)
		for join in join_request.join:
			if join == None: continue
			select_join_request = SelectRequest(join, is_join=True)
			join_result = await performJoin(db_instance, join_result, select_join_request, parent_name=join_request.store)

		if join_request.include and len(join_result) >= 1:
			for field_of_join in join_result[0]:
				if field_of_join == "id": continue
				already_selected[field_of_join] = join_result[0][field_of_join]
		else:
			already_selected[join_request.store] = join_result

	return last_result

class EmptyObject(object): pass
