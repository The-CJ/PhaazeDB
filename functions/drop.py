from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import os, json
from utils.errors import MissingNameField, ContainerNotFound
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class DropRequest(object):
	""" Contains informations for a valid drop request,
		does not mean the container must exist or other errors are impossible """
	def __init__(self, DBReq:DBRequest):
		self.container_name:str = None

		self.getContainterName(DBReq)

	def getContainterName(self, DBReq:DBRequest):
		self.container = DBReq.get("name", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingNameField()

async def drop(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to drop/delete container from DB and delete supercontainer if no container are left """

	# prepare request for a valid search
	try:
		DBDropRequest:DropRequest = DropRequest(DBReq)
		return await performDrop(cls, DBDropRequest)

	except (MissingNameField, ContainerNotFound) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performDrop(cls:"PhaazeDatabase", DBDropRequest:DropRequest) -> Response:
	""" Used to drop/delete container from DB (automaticly deletes supercontainer if necessary) """

	container_location = f"{cls.container_root}{DBDropRequest.container}.phaazedb"

	#does not exist
	if not os.path.isfile(container_location):
		raise ContainerNotFound(DBDropRequest.container)

	#remove from file system
	os.remove(container_location)

	#remove from active db
	CurrentlyLoadedContainer:Container = await cls.load(DBDropRequest.container, only_already_loaded=True)
	if CurrentlyLoadedContainer:
		await CurrentlyLoadedContainer.delete()

	#remove upper folder if empty
	await DropSupercontainer(cls, DBDropRequest.container)

	res:dict = dict(
		code=200,
		status="droped",
		msg=f"droped container '{DBDropRequest.container}'"
	)

	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"droped container '{DBDropRequest.container}'")
	return cls.response(status=200, body=json.dumps(res))

async def DropSupercontainer(cls:"PhaazeDatabase", container_name:str) -> None:

	supercontainer_path:str = os.path.dirname(container_name)
	folder_files:list = os.listdir(f"{cls.container_root}{supercontainer_path}")

	#folder is now empty -> remove
	if len(folder_files) == 0:
		# ignore database root dir
		if supercontainer_path == "": return

		os.rmdir(f"{cls.container_root}{supercontainer_path}")

		#check if the supercontainer of this is is now empty as well
		await DropSupercontainer(cls, supercontainer_path)