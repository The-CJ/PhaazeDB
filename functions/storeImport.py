from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, math
from utils.errors import MissingImportFile, ContainerAlreadyExists, SysCreateError, SysLoadError, ContainerNotFound, ImportNoActiveContainer, InvalidImportEntry, ImportEntryExists
from functions.create import makeNewContainer
from aiohttp.web import Request, Response
from aiohttp.web_request import FileField
from utils.loader import DBRequest
from utils.container import Container

class ImportRequest(object):
	"""
		Contains informations for a valid import request
		does not mean other errors are impossible,
		also it's a bridge class for all incomming data object,
		to be proccessed and inserted into the right db
	"""
	def __init__(self, DBReq:DBRequest, Database:"PhaazeDatabase"):
		self.fileObject:FileField = None
		self.Database:"PhaazeDatabase" = Database

		self.overwrite_container:bool = False
		self.overwrite_entrys:bool = False
		self.ignore_errors:bool = False

		# for processing
		self.current_container:str = None
		self.errors:list = []

		self.getFile(DBReq)
		self.getOverrides(DBReq)
		self.getIgnore(DBReq)

	def getFile(self, DBReq:DBRequest) -> None:
		self.fileObject = DBReq.get("phzdb", None)
		if not self.fileObject: raise MissingImportFile()

	def getOverrides(self, DBReq:DBRequest) -> None:
		self.overwrite_container = DBReq.get("overwrite_container", None)
		if type(self.overwrite_container) is not bool:
			self.overwrite_container = bool(self.overwrite_container)

		self.overwrite_entrys = DBReq.get("overwrite_entrys", None)
		if type(self.overwrite_entrys) is not bool:
			self.overwrite_entrys = bool(self.overwrite_entrys)

	def getIgnore(self, DBReq:DBRequest) -> None:
		self.ignore_errors = DBReq.get("ignore_errors", None)
		if type(self.ignore_errors) is not bool:
			self.ignore_errors = bool(self.ignore_errors)

	# following are "bride" functions
	async def processLine(self, line:bytes):
		try:
			if line.startswith(b"ENTRY:"): await self.proccessEntry(line)
			elif line.startswith(b"DEFAULT:"): await self.proccessDefault(line)
			elif line.startswith(b"CONTAINER:"): await self.proccessContainer(line)
			else: pass
		except json.decoder.JSONDecodeError as e:
			print(e)

	async def proccessEntry(self, line:bytes) -> bool:
		if not self.current_container:
			if self.ignore_errors:
				self.errors.append(f"can't insert entry, no active container -> skipping")
				return False
			else:
				raise ImportNoActiveContainer()

		entry:dict = json.loads(line[6:][:-2])
		DBContainer:Container = await self.Database.load(self.current_container)

		if DBContainer.status == "sys_error": raise SysLoadError(self.current_container)
		elif DBContainer.status == "not_found": raise ContainerNotFound(self.current_container)
		elif DBContainer.status == "success":
			pass

		# other than normal inserts, id's must me strict set back to previous value and not incremental
		entry_id:int = entry.get("id", 0)
		if not entry_id or not type(entry_id) == int:
			if self.ignore_errors:
				self.errors.append(f"broken entry -> skipping")
				return False
			else:
				raise InvalidImportEntry()

		# test if entry exist
		if DBContainer.data.get(entry_id, None) and not self.overwrite_entrys:
			if self.ignore_errors:
				self.errors.append(f"entry id: {entry_id} already exists -> skipping")
				return False
			else:
				raise ImportEntryExists()

		del entry["id"]
		DBContainer.data
		[entry_id] = entry

		if entry_id >= DBContainer.content.get("current_id", 0):
			DBContainer.content["current_id"] = entry_id + 1

		return True

	async def proccessDefault(self, line:bytes) -> bool:
		if not self.current_container:
			if self.ignore_errors:
				self.errors.append(f"can't set default, no active container -> skipping")
				return False
			else:
				raise ImportNoActiveContainer()

		default:dict = json.loads(line[8:][:-2])
		DBContainer:Container = await self.Database.load(self.current_container)

		if DBContainer.status == "sys_error": raise SysLoadError(self.current_container)
		elif DBContainer.status == "not_found": raise ContainerNotFound(self.current_container)
		elif DBContainer.status == "success":
			pass

		DBContainer.content["default"] = default

		return True

	async def proccessContainer(self, line:bytes) -> bool:
		DBContainer:Container = await self.Database.load(json.loads(line[10:][:-2]))
		if DBContainer.status != "not_found" and not self.overwrite_container:
			if self.ignore_errors:
				self.errors.append(f"container already exists: '{DBContainer.name}' -> set active anyway")
				self.current_container = DBContainer.name
				return False
			else:
				raise ContainerAlreadyExists(DBContainer.name)

		created:bool = await makeNewContainer(self.Database, DBContainer.name)

		# overwritten container get data purged
		if DBContainer.content:
			if DBContainer.content["data"]:
				DBContainer.content["data"] = dict()

		if not created:
			self.Database.PhaazeDBS.Logger.critical(f"create container '{DBContainer.name}' failed")
			raise SysCreateError(DBContainer.name)

		self.current_container = DBContainer.name
		return True

async def storeImport(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	"""
		Used to import data from file. file extention should be .phzdb
		but can be every type in therory
	"""
	# during import set save intervals to infinite and disable other actions
	cls.PhaazeDBS.Logger.info(f"Import from file started -> closing db for other actions")
	original_interval_time:int = cls.save_interval
	cls.save_interval = math.inf
	cls.active = False

	DBResult:Response = await storeImportHandler(cls, DBReq)

	# set db free
	cls.save_interval = original_interval_time
	cls.active = True
	cls.PhaazeDBS.Logger.info(f"Import from file complete -> reactivating")
	return DBResult

async def storeImportHandler(cls:"PhaazeDatabase", DBReq:DBRequest) -> Response:
	try:
		# prepare request for a valid import
		DBImportRequest:ImportRequest = ImportRequest(DBReq, cls)
		return await performImport(cls, DBImportRequest)

	except (MissingImportFile, ContainerAlreadyExists, SysCreateError, SysLoadError, ContainerNotFound, ImportNoActiveContainer, InvalidImportEntry, ImportEntryExists) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performImport(cls:"PhaazeDatabase", DBImportRequest:ImportRequest):
	print(type(DBImportRequest.fileObject))
	for line in DBImportRequest.fileObject.file:
		await DBImportRequest.processLine(line)

	await cls.storeAllContainer()

	res:dict = dict(
		code=200,
		status="imported",
		errors=DBImportRequest.errors,
		ignore_errors=DBImportRequest.ignore_errors,
		overwrite_container=DBImportRequest.overwrite_container,
		overwrite_entrys=DBImportRequest.overwrite_entrys
	)

	return cls.response(status=200, body=json.dumps(res))
