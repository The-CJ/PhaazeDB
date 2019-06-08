from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, math, copy
from utils.errors import MissingOfField, MissingStoreInJoin, ContainerNotFound, SysLoadError, InvalidJoin, InvalidLimit
from utils.loader import DBRequest
from utils.container import Container
from aiohttp.web import Request, Response

class SelectRequest(object):
	"""
		Contains informations for a valid select request,
		does not mean the container exists or where statement has right syntax
	"""
	def __init__(self, DBReq:DBRequest, is_join:bool=False):
		self.container:str = None
		self.where:str = ""
		self.fields:list = []
		self.offset:int = 0
		self.limit:int = math.inf
		self.store:str = None
		self.join:list[dict] = []
		self.is_join:bool = is_join
		self.include:bool = False

		self.getContainter(DBReq)
		self.getWhere(DBReq)
		self.getFields(DBReq)
		self.getOffset(DBReq)
		self.getLimit(DBReq)
		self.getStore(DBReq)
		self.getJoin(DBReq)
		self.getInclude(DBReq)

	def getContainter(self, DBReq) -> None:
		self.container = DBReq.get("of", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingOfField()

	def getWhere(self, DBReq) -> None:
		self.where = DBReq.get("where", "")

	def getFields(self, DBReq) -> None:
		self.fields = DBReq.get("fields", None)
		if type(self.fields) is str:
			self.fields = self.fields.split(",")
		if type(self.fields) is not list:
			self.fields = []

	def getOffset(self, DBReq) -> None:
		self.offset = DBReq.get("offset", -1)
		if type(self.offset) is str:
			if self.offset.isdigit():
				self.offset = int(self.offset)

		if type(self.offset) is not int:
			self.offset = -1

	def getLimit(self, DBReq) -> None:
		self.limit = DBReq.get("limit", math.inf)
		if type(self.limit) is str:
			if self.limit.isdigit():
				self.limit = int(self.limit)

		if type(self.limit) is not int:
			self.limit = math.inf

		if self.limit <= 0:
			raise InvalidLimit()

	def getStore(self, DBReq) -> None:
		self.store = DBReq.get("store", None)
		if type(self.store) is not str:
			self.store = None

		if not self.store and self.is_join:
			raise MissingStoreInJoin()

	def getJoin(self, DBReq) -> None:
		self.join = DBReq.get("join", None)
		if type(self.join) is str:
			try:
				self.join = json.loads(self.join)
			except:
				raise InvalidJoin()
		if type(self.join) != list: self.join = [self.join]

	def getInclude(self, DBReq) -> None:
		self.include = bool(DBReq.get("include", False))

async def select(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest):
	"""
		Used to select data from ad DB container and give it back, may also include joins to other tables
	"""
	# prepare request for a valid search
	try:
		DBSelectRequest:SelectRequest = SelectRequest(DBReq)
		return await performSelect(cls, DBSelectRequest)

	except (ContainerNotFound, MissingOfField, SysLoadError, InvalidLimit, MissingStoreInJoin) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performSelect(cls:"PhaazeDatabase", DBSelectRequest:SelectRequest):

	result:dict = await getDataFromContainer(cls, DBSelectRequest)

	for join in DBSelectRequest.join:
		if join == None: continue
		DBSelectJoinRequest:SelectRequest = SelectRequest(join, is_join=True)
		result["entry_list"] = await performJoin(cls, result["entry_list"], DBSelectJoinRequest, parent_name=DBSelectRequest.store)

	res:dict = dict(
		code=200,
		status="selected",

		hits=result["hits"],
		hits_field=result["hits_field"],
		total=result["total"],
		data=result["entry_list"]
	)
	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"selected {str(result['hits'])} entry(s) from '{DBSelectRequest.container}'")
	return cls.response(status=200, body=json.dumps(res))

async def getDataFromContainer(cls:"PhaazeDatabase", DBSelectRequest:SelectRequest, parent_name:str=None, parent_entry:dict=None) -> dict:
	if DBSelectRequest.container in [None, ""]:
		return dict(
			entry_list = [],
			hits = 0,
			hits_field = 0,
			total = 0
		)

	DBContainer:Container = await cls.load(DBSelectRequest.container)

	if DBContainer.status == "sys_error": raise SysLoadError(DBSelectRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBSelectRequest.container)
	elif DBContainer.status == "success":
		pass

	# return values
	result:list = []
	hits:int = 0
	hits_field:int = 0

	found:int = 0
	default_set:dict = DBContainer.default

	#go through all entrys
	for entry_id in DBContainer.data:
		entry:dict = DBContainer.data[entry_id]
		entry['id'] = entry_id

		# where dont hit entry, means skip, we dont need it
		if not await checkWhere(where=DBSelectRequest.where, parent_name=parent_name, parent_entry=parent_entry, check_entry=entry, check_name=DBSelectRequest.store):
			continue

		found += 1
		if DBSelectRequest.offset >= found:
			continue

		# copy entry before further actions, so the entry in the db itself does not get the default set added to permanent memory
		# TODO: add own custom object to make better where statements
		entry = copy.deepcopy(entry)

		# complete entry
		for default_key in default_set:
			if entry.get(default_key, EmptyObject) == EmptyObject:
				entry[default_key] = DBContainer.default[default_key]

		# only gather what the user wants
		requested_fields:list = await getFields(entry, DBSelectRequest.fields)

		hits += 1
		hits_field += len(requested_fields)

		result.append( requested_fields )

		if hits >= DBSelectRequest.limit:
			break

	return dict(
		entry_list = result,
		hits = hits,
		hits_field = hits_field,
		total = len(DBContainer.data)
	)

async def checkWhere(where="", parent_entry:dict=None, parent_name:str=None, check_entry:dict=None, check_name:str=None) -> bool:

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

async def getFields(data:dict, fields:list) -> dict:
	if not fields: return data

	requested_fields:dict = dict()
	for field in fields:
		requested_fields[field] = data.get(field, None)

	return requested_fields

async def performJoin(cls:"PhaazeDatabase", last_result:list, DBSelectJoinRequest:SelectRequest, parent_name:str=None) -> list:

	DBContainer:Container = await cls.load(DBSelectJoinRequest.container)

	if DBContainer.status == "sys_error": raise SysLoadError(DBSelectJoinRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBSelectJoinRequest.container)
	elif DBContainer.status == "success":
		pass

	# for every already selected entry, take the data and go in the next container
	for already_selected in last_result:

		result:dict = await getDataFromContainer(cls, DBSelectJoinRequest, parent_name=parent_name, parent_entry=already_selected)
		for join in DBSelectJoinRequest.join:
			if join == None: continue
			DBSelectAnotherJoinRequest:SelectRequest = SelectRequest(join, is_join=True)
			result["entry_list"] = await performJoin(cls, result["entry_list"], DBSelectAnotherJoinRequest, parent_name=DBSelectJoinRequest.store)

		if DBSelectJoinRequest.include and len(result["entry_list"]) >= 1:
			for field_of_join in result["entry_list"][0]:
				if field_of_join == "id": continue
				already_selected[field_of_join] = result["entry_list"][0][field_of_join]
		else:
			already_selected[DBSelectJoinRequest.store] = result["entry_list"]

	return last_result

class EmptyObject(object): pass
