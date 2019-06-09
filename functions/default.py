from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json
from utils.errors import MissingNameField, InvalidContent, SysLoadError, ContainerNotFound, SysStoreError
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class DefaultRequest(object):
	""" Contains informations for a valid container default request,
		does not mean the container may not already be existing or other errors are impossible """
	def __init__(self, DBReq:DBRequest):
		self.container:str = None
		self.default_content:dict = None

		self.getContainterName(DBReq)
		self.getContainterTemplate(DBReq)

	def getContainterName(self, DBReq:DBRequest) -> None:
		self.container = DBReq.get("name", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingNameField()

	def getContainterTemplate(self, DBReq:DBRequest) -> None:
		self.default_content = DBReq.get("content", "")

		if type(self.default_content) is str:
			try:
				self.default_content = json.loads(self.default_content)
			except:
				raise InvalidContent()

		if type(self.default_content) is not dict:
			raise InvalidContent()

async def default(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	"""
		Used to set a new object as default for a container,
		values in default set always get added to a select request, (if requested in 'fields')
		so values will always be there
	"""

	# prepare request for a valid search
	try:
		DBDefaultRequest:DefaultRequest = DefaultRequest(DBReq)
		return await performDefault(cls, DBDefaultRequest)

	except (MissingNameField, InvalidContent, SysStoreError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performDefault(cls:"PhaazeDatabase", DBDefaultRequest:DefaultRequest) -> Response:

	#unnamed key
	if DBDefaultRequest.default_content.get('', EmptyObject) != EmptyObject:
		raise InvalidContent(True)

	DBContainer:Container = await cls.load(DBDefaultRequest.container)

	if DBContainer.status == "sys_error": raise SysLoadError(DBDefaultRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBDefaultRequest.container)
	elif DBContainer.status == "success":
		pass

	# actully set it
	DBContainer.content["default"] = DBDefaultRequest.default_content

	#save everything
	success = await cls.store(DBContainer)

	if not success:
		cls.Server.Logger.critical(f"setting default set for container '{DBDefaultRequest.container}' failed")
		raise SysStoreError(DBDefaultRequest.container)

	res = dict(
		code=200,
		status="default set",
		container=DBDefaultRequest.container,
		default=DBDefaultRequest.default_content,
		msg=f"default set for container '{DBDefaultRequest.container}'"
	)
	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"default set for container '{DBDefaultRequest.container}'")
	return cls.response(status=200, body=json.dumps(res))

class EmptyObject(): pass