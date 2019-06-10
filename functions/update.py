from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, math
from utils.errors import MissingOfField, InvalidLimit, MissingUpdateContent, SysLoadError, ContainerNotFound, InvalidUpdateExec, SysStoreError
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class UpdateEntry(dict):
	"""
		Class is used to wrap dict object database entrys so its impossible
		to set integre as a dict key
	 	get's reverted to normal dict after update is finished
	"""
	def __setitem__(self, key, value):
		super().__setitem__(str(key), value)
	def __getitem__(self, key):
		return super().__getitem__(str(key))

class UpdateRequest(object):
	"""
		Contains informations for a valid update request,
		does not mean the container exists or where statement has right syntax
	"""
	def __init__(self, DBReq:DBRequest):
		self.container:str = None
		self.where:str = ""
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None
		self.method:str = ""
		self.content:all = None

		self.getContainter(DBReq)
		self.getWhere(DBReq)
		self.getOffset(DBReq)
		self.getLimit(DBReq)
		self.getStore(DBReq)
		self.getUpdate(DBReq)

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

	def getUpdate(self, DBReq:DBRequest) -> None:
		self.content = DBReq.get("content", None)

		if type(self.content) is dict:
			self.method = "dict"
		elif type(self.content) is str:
			self.method = "str"
		else:
			raise MissingUpdateContent()

async def update(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to update entry fields in a existing container """

	# prepare request for a valid search
	try:
		DBUpdateRequest:UpdateRequest = UpdateRequest(DBReq)
		return await performUpdate(cls, DBUpdateRequest)

	except (MissingOfField, InvalidLimit, MissingUpdateContent, SysLoadError, SysStoreError, ContainerNotFound, InvalidUpdateExec) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performUpdate(cls:"PhaazeDatabase", DBUpdateRequest:UpdateRequest) -> Response:

	result:dict = await updateDataInContainer(cls, DBUpdateRequest)

	res = dict(
		code=201,
		status="updated",

		hits=result["hits"],
		total=result["total"],
	)
	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"updated {str(result['hits'])} entry(s) from '{DBUpdateRequest.container}'")
	return cls.response(status=201, body=json.dumps(res))

async def updateDataInContainer(cls:"PhaazeDatabase", DBUpdateRequest:UpdateRequest) -> dict:

	#unnamed key
	if DBUpdateRequest.method == "dict" and DBUpdateRequest.content.get("", EmptyObject) != EmptyObject:
		raise MissingUpdateContent(True)

	#get current container from db
	DBContainer:Container = await cls.load(DBUpdateRequest.container)

	#error handling
	if DBContainer.status == "sys_error": raise SysLoadError(DBUpdateRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBUpdateRequest.container)
	elif DBContainer.status == "success":
		pass

	#return values
	hits:int = 0

	#go through all entrys
	found:int = 0
	for entry_id in DBContainer.data:
		entry:dict = DBContainer.data[entry_id]
		entry['id'] = entry_id

		# where don't hit on entry, means skip, we dont need it
		if not await checkWhere(where=DBUpdateRequest.where, check_name=DBUpdateRequest.store, check_entry=entry, ):
			continue

		found += 1
		if DBUpdateRequest.offset >= found:
			continue

		# update the entry with new content
		DBContainer.data[entry_id] = await updateEntry(entry, DBUpdateRequest)

		hits += 1

		if hits >= DBUpdateRequest.limit:
			break

	#save everything
	success:bool = await cls.store(DBContainer)

	if not success:
		cls.PhaazeDBS.Logger.critical(f"updateing data in container '{DBUpdateRequest.container}' failed")
		raise SysStoreError(DBUpdateRequest.container)

	return dict(
		hits = hits,
		total = len(DBContainer.data)
	)

async def updateEntry(data:dict, DBUpdateRequest:UpdateRequest) -> dict:
	if DBUpdateRequest.method == "dict":
		for new_data_key in DBUpdateRequest.content:
			data[str(new_data_key)] = DBUpdateRequest.content[new_data_key]

	elif DBUpdateRequest.method == "str":
		# wrap db entry, to ensure dict keys are strings
		data = UpdateEntry(data)
		if DBUpdateRequest.store:
			loc = locals()
			loc[DBUpdateRequest.store] = data

		try:
			exec(DBUpdateRequest.content)
		except Exception as e:
			raise InvalidUpdateExec(str(e))

	return dict(data)

async def checkWhere(where:str="", check_name:str=None, check_entry:dict=None) -> bool:
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
