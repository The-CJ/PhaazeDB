from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import os, json
from datetime import datetime
from utils.errors import MissingNameField, ContainerAlreadyExists, SysCreateError
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class CreateRequest(object):
	""" Contains informations for a valid create request,
		does not mean the container may not already be existing or other errors are impossible """
	def __init__(self, DBReq:DBRequest):
		self.container:str = None

		self.getContainterName(DBReq)

	def getContainterName(self, DBReq:DBRequest):
		self.container = DBReq.get("name", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingNameField()

async def create(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to create new container in the database (automaticly creates supercontainer if necessary) """

	# prepare request for a valid search
	try:
		DBCreateRequest:CreateRequest = CreateRequest(DBReq)
		return await performCreate(cls, DBCreateRequest)

	except (MissingNameField, ContainerAlreadyExists, SysCreateError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performCreate(cls:"PhaazeDatabase", DBCreateRequest:CreateRequest) -> Response:
	container_location = f"{cls.container_root}{DBCreateRequest.container}.phaazedb"

	#already exist
	if os.path.isfile(container_location):
		raise ContainerAlreadyExists(DBCreateRequest.container)

	success = await makeNewContainer(cls, DBCreateRequest.container)

	if not success:
		cls.PhaazeDBS.Logger.critical(f"create container '{DBCreateRequest.container}' failed")
		raise SysCreateError(DBCreateRequest.container)

	res = dict(
		code=201,
		status="created",

		msg=f"created container '{DBCreateRequest.container}'"
	)
	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"created container '{DBCreateRequest.container}'")
	return cls.response(status=201, body=json.dumps(res))

async def makeNewContainer(cls, container_name:str) -> bool:
	new_content:dict = dict (
		current_id = 1,
		data = dict(),
		default = dict(),
		creation_date = str(datetime.now())
	)

	NewContainer:Container = Container(cls, container_name, status="new", content=new_content)
	created = await cls.store(NewContainer, create=True)

	return created
