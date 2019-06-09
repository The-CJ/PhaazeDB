from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json
from utils.errors import MissingNameField, SysLoadError, ContainerNotFound
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class DescribeRequest(object):
	""" Contains informations for a valid describe request,
		does not mean the container exists or other errors are impossible """
	def __init__(self, db_req):
		self.container:str = None

		self.getContainterName(db_req)

	def getContainterName(self, db_req):
		self.container = db_req.get("name", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: raise MissingNameField()

async def describe(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to get the defaults value list of a container, pretty much the counterpart to self.default """

	# prepare request for a valid search
	try:
		DBDescribeRequest:DescribeRequest = DescribeRequest(DBReq)
		return await performDescribe(cls, DBDescribeRequest)

	except (MissingNameField, SysLoadError, ContainerNotFound) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performDescribe(cls:"PhaazeDatabase", DBDescribeRequest:DescribeRequest):

	DBContainer:Container = await cls.load(DBDescribeRequest.container)

	if DBContainer.status == "sys_error": raise SysLoadError(DBDescribeRequest.container)
	elif DBContainer.status == "not_found": raise ContainerNotFound(DBDescribeRequest.container)
	elif DBContainer.status == "success":
		pass

	default_template:dict = DBContainer.default

	#awnser
	res = dict(
		code=200,
		status="described",
		container=DBDescribeRequest.container,
		default=default_template,
		msg=f"described container '{DBDescribeRequest.container}'"
	)

	if cls.PhaazeDBS.action_logging:
		cls.PhaazeDBS.Logger.info(f"described container '{DBDescribeRequest.container}'")
	return cls.response(status=200, body=json.dumps(res))

class EmptyObject(): pass
