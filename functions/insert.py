from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json
from utils.errors import MissingIntoField, InvalidContent, SysLoadError, SysStoreError, ContainerNotFound, ContainerBroken
from utils.container import Container
from utils.loader import DBRequest
from aiohttp.web import Request, Response

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

async def insert(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to insert a new entry into a existing container """

	# prepare request for a valid insert
	try:
		DBInsertRequest:InsertRequest = InsertRequest(DBReq)
		return await performInsert(cls, DBInsertRequest)

	except (MissingIntoField, InvalidContent, ContainerNotFound, ContainerBroken, SysLoadError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performInsert(cls:"PhaazeDatabase", DBInsertRequest:InsertRequest) -> Response:

	# unnamed key
	if DBInsertRequest.content.get('', EmptyObject) != EmptyObject:
		raise InvalidContent(True)

	# get current container from db
	DBContainer:Container = await cls.load(DBInsertRequest.container)

	# error handling
	if DBContainer.status == "sys_error": raise SysLoadError(DBInsertRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBInsertRequest.container)
	elif DBContainer.status == "success":
		pass

	# get current_id
	current_id_index:int = DBContainer.currentid
	if not current_id_index:
		raise ContainerBroken(DBInsertRequest.container)

	#add entry
	# DBInsertRequestcontent['id'] = current_id_index
	DBContainer.data[current_id_index] = DBInsertRequest.content
	# Container.content[current_id_index] = DBInsertRequest.content

	#increase id
	DBContainer.increaseId()

	#save everything
	success = await cls.store(DBInsertRequest.container, DBContainer)

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
