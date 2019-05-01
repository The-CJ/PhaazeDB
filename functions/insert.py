import asyncio, json
from utils.errors import MissingIntoField, InvalidContent

class InsertRequest(object):
	""" Contains informations for a valid insert request,
		does not mean the container exists """
	def __init__(self, db_req):
		self.container:str = None
		self.content:dict = dict()

		self.getContainter(db_req)
		self.getContent(db_req)

	def getContainter(self, db_req):
		self.container = db_req.get("into", "")
		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingIntoField

	def getContent(self, db_req):
		self.content = db_req.get("content", None)

		if type(self.content) is str:
			try:
				self.content = json.loads(self.content)
			except:
				raise InvalidContent()

		if type(self.content) is not dict:
			raise InvalidContent()

async def insert(self, request):
	""" Used to insert a new entry into a existing container """

	# prepare request for a valid insert
	try:
		insert_request = InsertRequest(request.db_request)
		return await performInsert(self, insert_request)

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performInsert(db_instance, insert_request):

	print(vars(insert_request))

	return None

	#unnamed key
	if content.get('', dummy) != dummy:
		res = dict(
			code=400,
			status="error",
			msg="field 'content' has a unnamed json-object key"
		)
		return self.response(status=400, body=json.dumps(res))

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

	#get current_id
	_id_ = container['current_id']

	#add entry
	container['data'][_id_] = content
	content['id'] = _id_

	#increase id
	container['current_id'] = _id_ + 1

	# # #

	#save everything
	finished = await self.store(table_name, container)

	if finished:
		res = dict(
			code=201,
			status="inserted",
			msg=f"successfully inserted into container '{table_name}'",
			data=content
		)
		if self.log != False:
			self.logger.info(f"insert entry into '{table_name}': {str(content)}")
		return self.response(status=201, body=json.dumps(res))

	else:
		# this SHOULD never happen, but hey... just in case
		res = dict(
			code=500,
			status="error",
			msg="DB could not save your data."
		)
		if self.log != False:
			self.logger.critical(f"insert entry into '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))

class dummy(object):
	pass
