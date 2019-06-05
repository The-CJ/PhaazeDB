import json
from utils.errors import MissingIntoField, InvalidContent, SysLoadError, SysStoreError, ContainerNotFound, ContainerBroken
from utils.loader import DBRequest

class InsertRequest(object):
	""" Contains informations for a valid insert request,
		does not mean the container exists """
	def __init__(self, DBReq:DBRequest):
		self.container:str = None
		self.content:dict = dict()

		self.getContainter(DBReq)
		self.getContent(DBReq)

	def getContainter(self, DBReq:DBRequest) -> None:
		self.container = DBReq.get("into", "")
		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingIntoField()

	def getContent(self, DBReq:DBRequest) -> None:
		self.content = DBReq.get("content", None)

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

	except (MissingIntoField, InvalidContent, ContainerNotFound, ContainerBroken, SysLoadError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performInsert(db_instance, insert_request):

	#unnamed key
	if insert_request.content.get('', EmptyObject) != EmptyObject:
		raise InvalidContent(True)

	#get current container from db
	container = await db_instance.load(insert_request.container)

	#error handling
	if container.status == "sys_error": raise SysLoadError(insert_request.container)
	elif container.status == "not_found": raise ContainerNotFound(insert_request.container)
	elif container.status == "success":	container = container.content

	#get current_id
	current_id_index = container.get('current_id',  None)
	if current_id_index == None: raise ContainerBroken(insert_request.container)

	#add entry
	insert_request.content['id'] = current_id_index
	container['data'][current_id_index] = insert_request.content

	#increase id
	container['current_id'] = current_id_index + 1

	#save everything
	success = await db_instance.store(insert_request.container, container)

	if not success:
		db_instance.Server.Logger.critical(f"inserting data into container '{insert_request.container}' failed")
		raise SysStoreError(insert_request.container)

	res = dict(
		code=201,
		status="inserted",
		msg=f"successfully inserted into container '{insert_request.container}'",
		data=insert_request.content
	)

	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"insert entry into '{insert_request.container}': {str(insert_request.content)}")
	return db_instance.response(status=201, body=json.dumps(res))

class EmptyObject(object): pass
