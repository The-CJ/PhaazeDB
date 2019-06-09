from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, os
from utils.errors import CantAccessContainer, SysLoadError, ContainerNotFound
from functions.show import getContainer
from aiohttp.web import Request, Response, StreamResponse
from utils.loader import DBRequest
from utils.container import Container

class ExportRequest(object):
	""" Contains informations for a valid export request,
		does not mean the container exists """
	def __init__(self, DBReq:DBRequest, Original:Request):
		self.container:str = None
		self.recursive:bool = False
		self.WebRequest:Request = Original

		self.getRecursive(DBReq)
		self.getContainter(DBReq)

	def getRecursive(self, DBReq:DBRequest):
		self.recursive = DBReq.get("recursive",None)
		if type(self.recursive) is not bool:
			self.recursive = bool(self.recursive)

	def getContainter(self, DBReq:DBRequest):
		self.container = DBReq.get("container", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: self.container = ""

async def storeExport(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response or StreamResponse:
	""" Used to export (super)container into a .pdb file and import it later again """

	# prepare request for a valid search
	try:
		DBExportRequest:ExportRequest = ExportRequest(DBReq, WebRequest)
		return await performStoreExport(cls, DBExportRequest)

	except (CantAccessContainer, SysLoadError, ContainerNotFound) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performStoreExport(cls:"PhaazeDatabase", DBExportRequest:ExportRequest) -> Response or StreamResponse:
	check_location:str = f"{cls.container_root}{DBExportRequest.container}"

	if os.path.exists(f"{check_location}.phaazedb"):
		return await performExportDataGather(cls, DBExportRequest, [DBExportRequest.container])

	if not os.path.exists(check_location):
		res = dict(
			code=400,
			status="error",
			msg=f"no (super)container found: '{DBExportRequest.container}'",
		)
		return cls.response(status=400, body=json.dumps(res))

	root:dict = {'supercontainer': {},'container': [], 'unusable': []}
	tree:dict = await getContainer(root, check_location, recursive=DBExportRequest.recursive)

	container_list:list = splitTree(tree, before=f"{DBExportRequest.container}/")

	return await performExportDataGather(cls, DBExportRequest, container_list)

def splitTree(root:dict, before:str="") -> list:
	container:list = [f"{before}{con}" for con in root['container']]
	for log in root["supercontainer"]:
		supercontainer:list = splitTree(root["supercontainer"][log], before=before+log+"/")
		for s in supercontainer: container.append(s)

	return container

async def performExportDataGather(cls:"PhaazeDatabase", DBExportRequest:ExportRequest, export_list:list) -> StreamResponse:
	ReturnStreamFile:StreamResponse = StreamResponse()
	ReturnStreamFile.content_type = "application/octet-stream"

	name:str = DBExportRequest.container if DBExportRequest.container else "Database"
	ReturnStreamFile.headers["CONTENT-DISPOSITION"] = f"attachment; filename={name}.phzdb"
	ReturnStreamFile.set_status(200, reason="OK")
	await ReturnStreamFile.prepare(DBExportRequest.WebRequest)

	for container in export_list:
		DBContainer:Container = await cls.load(container)

		await ReturnStreamFile.write( bytes("CONTAINER:"+json.dumps(DBContainer.name)+";\n", "UTF-8") )

		if DBContainer.status == "sys_error": raise SysLoadError(DBExportRequest.container)
		elif DBContainer.status == "not_found": raise ContainerNotFound(DBExportRequest.container)
		elif DBContainer.status == "success":
			pass

		await ReturnStreamFile.write( bytes("DEFAULT:"+json.dumps(DBContainer.default)+";\n", "UTF-8") )

		for entry_id in DBContainer.data:
			entry:dict = DBContainer.data[entry_id]
			entry['id'] = entry_id

			await ReturnStreamFile.write( bytes("ENTRY:"+json.dumps(entry)+";\n", "UTF-8") )

	await ReturnStreamFile.write_eof()
	cls.PhaazeDBS.Logger.info(f"exported database: path={DBExportRequest.container}, recursive={str(DBExportRequest.recursive)}")
	return ReturnStreamFile
