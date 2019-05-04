import json, math
from utils.errors import MissingOfField, InvalidLimit, MissingUpdateContent

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

	except (MissingOfField, InvalidLimit, MissingUpdateContent) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performUpdate(db_instance, update_request):

	hits, total = updateDataInContainer(db_instance, update_request)

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

	if update_request.method == "dict" and update_request.content.get("", EmptyObject) != EmptyObject:
		raise MissingUpdateContent(True)



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

class EmptyObject(): pass
