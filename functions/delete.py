import json, math
from utils.errors import MissingOfField, InvalidLimit, SysLoadError, ContainerNotFound, SysStoreError

class DeleteRequest(object):
	""" Contains informations for a valid delete request,
		does not mean the container may not already be existing or other errors are impossible """
	def __init__(self, db_req):
		self.container:str = None
		self.where:str = ""
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None

		self.getContainter(db_req)
		self.getWhere(db_req)
		self.getOffset(db_req)
		self.getLimit(db_req)
		self.getStore(db_req)

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

async def delete(self, request):
	""" Used to delete entrys from the database """

	# prepare request for a valid search
	try:
		delete_request = DeleteRequest(request.db_request)
		return await performDelete(self, delete_request)

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performDelete(db_instance, delete_request):

	container = await db_instance.load(delete_request.container)

	#error handling
	if container.status == "sys_error": raise SysLoadError(delete_request.container)
	elif container.status == "not_found": raise ContainerNotFound(delete_request.container)
	elif container.status == "success":	container = container.content

	hits = 0
	found = 0

	# list(data) -> for a copy of data, so there is no RuntimeError because changing list size
	for entry_id in list(container.get("data", [])):
		entry = container['data'][entry_id]
		entry['id'] = entry_id

		# where dont hit entry, means skip, we dont need it
		if not await checkWhere(where=delete_request.where, check_entry=entry, check_name=delete_request.store):
			continue

		found += 1
		if delete_request.offset >= found:
			continue

		# delete entry
		del container['data'][entry_id]
		hits += 1

		if hits >= delete_request.limit:
			break

	#save everything
	success = await db_instance.store(delete_request.container, container)

	if not success:
		db_instance.Server.Logger.critical(f"deleting data in container '{delete_request.container}' failed")
		raise SysStoreError(delete_request.container)

	res = dict(
		code=201,
		status="deleted",

		hits=hits,
		total=len( container.get('data', []) ),
	)

	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"deleted {str(hits)} entry(s) from '{delete_request.container}'")
	return db_instance.response(status=201, body=json.dumps(res))

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
