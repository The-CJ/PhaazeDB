import json, math
from utils.errors import MissingOfField, InvalidLimit, MissingUpdateContent, SysLoadError, ContainerNotFound, InvalidUpdateExec, SysStoreError

class UpdateRequest(object):
	""" Contains informations for a valid update request,
		does not mean the container exists or where statement has right syntax """
	def __init__(self, db_req):
		self.container:str = None
		self.where:str = ""
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None
		self.method:str = ""
		self.content:all = None

		self.getContainter(db_req)
		self.getWhere(db_req)
		self.getOffset(db_req)
		self.getLimit(db_req)
		self.getStore(db_req)
		self.getUpdate(db_req)

	def getContainter(self, db_req):
		self.container = db_req.get("of", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingOfField()

	def getWhere(self, db_req):
		self.where = db_req.get("where", "")

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

	def getUpdate(self, db_req):
		self.content = db_req.get("content", None)

		if type(self.content) is dict:
			self.method = "dict"
		elif type(self.content) is str:
			self.method = "str"
		else:
			raise MissingUpdateContent()

async def update(self, request):
	""" Used to update entry fields in a existing container """

	# prepare request for a valid search
	try:
		update_request = UpdateRequest(request.db_request)
		return await performUpdate(self, update_request)

	except (MissingOfField, InvalidLimit, MissingUpdateContent, SysLoadError, SysStoreError, ContainerNotFound, InvalidUpdateExec) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performUpdate(db_instance, update_request):

	hits, total = await updateDataInContainer(db_instance, update_request)

	res = dict(
		code=201,
		status="updated",

		hits=hits,
		total=total,
	)
	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"updated {str(hits)} entry(s) from '{update_request.container}'")
	return db_instance.response(status=201, body=json.dumps(res))

async def updateDataInContainer(db_instance, update_request):

	#unnamed key
	if update_request.method == "dict" and update_request.content.get("", EmptyObject) != EmptyObject:
		raise MissingUpdateContent(True)

	#get current container from db
	container = await db_instance.load(update_request.container)

	#error handling
	if container.status == "sys_error": raise SysLoadError(update_request.container)
	elif container.status == "not_found": raise ContainerNotFound(update_request.container)
	elif container.status == "success":	container = container.content

	#return values
	hits = 0

	#go through all entrys
	found = 0
	for entry_id in container.get('data', []):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		# where dont hit entry, means skip, we dont need it
		if not await checkWhere(where=update_request.where, check_entry=entry, check_name=update_request.store):
			continue

		found += 1
		if update_request.offset >= found:
			continue

		# update the entry with new content
		entry = await updateEntry(entry, update_request)

		hits += 1

		if hits >= update_request.limit:
			break

	#save everything
	success = await db_instance.store(update_request.container, container)

	if not success:
		db_instance.Server.Logger.critical(f"updateing data in container '{update_request.container}' failed")
		raise SysStoreError(update_request.container)

	return hits, len(container.get('data', []) )

async def updateEntry(data, update_request):
	if update_request.method == "dict":
		for new_data_key in update_request.content:
			data[new_data_key] = update_request.content[new_data_key]

	elif update_request.method == "str":
		if update_request.store:
			loc = locals()
			loc[update_request.store] = data

		try:
			exec(update_request.content)
		except Exception as e:
			raise InvalidUpdateExec(str(e))

	return data

async def checkWhere(where="", check_entry=None, check_name=None):
	if not where:
		return True

	if not check_name:
		check_name = "data"

	loc = locals()
	loc[check_name] = check_entry

	try:
		if eval(where):
			return True
		else:
			return False
	except:
		return False

class EmptyObject(): pass
