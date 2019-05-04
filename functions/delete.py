import json, math
from utils.errors import MissingOfField, InvalidLimit

class DeleteRequest(object):
	""" Contains informations for a valid delete request,
		does not mean the container may not already be existing or other errors are iompossible """
	def __init__(self, db_req):
		self.container:str = None
		self.where:str = ""
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None

		self.getContainter(db_req)
		self.where(db_req)
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

async def performDelete(db_instance, select_request):

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
		if self.log != False:
			self.logger.info(f"deleted {str(hits)} entry(s) from '{table_name}'")
		return self.response(status=201, body=json.dumps(res))

	else:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not save your data."
		)
		if self.log != False:
			self.logger.critical(f"deleted {str(hits)} entry(s) from '{table_name}'")
		return self.response(status=500, body=json.dumps(res))


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
