from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, math
from utils.errors import MissingOfField, InvalidLimit, SysLoadError, ContainerNotFound, SysStoreError
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class DeleteRequest(object):
	""" Contains informations for a valid delete request,
		does not mean the container may not already be existing or other errors are impossible """
	def __init__(self, DBReq:DBRequest):
		self.container:str = None
		self.where:str = ""
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None

		self.getContainter(DBReq)
		self.getWhere(DBReq)
		self.getOffset(DBReq)
		self.getLimit(DBReq)
		self.getStore(DBReq)

	def getContainter(self, DBReq:DBRequest) -> None:
		self.container = DBReq.get("of", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingOfField()

	def getWhere(self, DBReq:DBRequest) -> None:
		self.where = DBReq.get("where", "")

	def getOffset(self, DBReq:DBRequest) -> None:
		self.offset = DBReq.get("offset", -1)
		if type(self.offset) is str:
			if self.offset.isdigit():
				self.offset = int(self.offset)

		if type(self.offset) is not int:
			self.offset = -1

	def getLimit(self, DBReq:DBRequest) -> None:
		self.limit = DBReq.get("limit", math.inf)
		if type(self.limit) is str:
			if self.limit.isdigit():
				self.limit = int(self.limit)

		if type(self.limit) is not int:
			self.limit = math.inf

		if self.limit <= 0:
			raise InvalidLimit()

	def getStore(self, DBReq:DBRequest) -> None:
		self.store = DBReq.get("store", None)
		if type(self.store) is not str:
			self.store = None

async def delete(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to delete entrys from the database """

	# prepare request for a valid search
	try:
		DBDeleteRequest:DeleteRequest = DeleteRequest(DBReq)
		return await performDelete(cls, DBDeleteRequest)

	except (MissingOfField, MissingOfField, SysLoadError, ContainerNotFound, SysStoreError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performDelete(cls:"PhaazeDatabase", DBDeleteRequest:DeleteRequest) -> Response:

	DBContainer:Container = await cls.load(DBDeleteRequest.container)

	#error handling
	if DBContainer.status == "sys_error": raise SysLoadError(DBDeleteRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBDeleteRequest.container)
	elif DBContainer.status == "success":
		pass

	hits:int = 0
	found:int = 0

	# list(data) -> for a copy of data, so there is no RuntimeError because changing list size
	for entry_id in list(DBContainer.data):
		entry:dict = DBContainer.data[entry_id]
		entry['id'] = entry_id

		# where don't hit on entry, means skip, we dont need it
		if not await checkWhere(where=DBDeleteRequest.where, check_entry=entry, check_name=DBDeleteRequest.store):
			continue

		found += 1
		if DBDeleteRequest.offset >= found:
			continue

		# delete entry
		del DBContainer.data[entry_id]
		hits += 1

		if hits >= DBDeleteRequest.limit:
			break

	#save everything
	success = await cls.store(DBContainer)

	if not success:
		cls.PhaazeDBS.Logger.critical(f"deleting data in container '{DBDeleteRequest.container}' failed")
		raise SysStoreError(DBDeleteRequest.container)

	res = dict(
		code=201,
		status="deleted",

		hits=hits,
		total=len( DBContainer.data ),
	)

	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"deleted {str(hits)} entry(s) from '{DBDeleteRequest.container}'")
	return cls.response(status=201, body=json.dumps(res))

async def checkWhere(where:str="", check_entry:dict=None, check_name:str=None) -> bool:
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
