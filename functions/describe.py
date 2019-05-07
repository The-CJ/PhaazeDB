import json
from utils.errors import MissingNameField, SysLoadError, ContainerNotFound

class DescribeRequest(object):
	""" Contains informations for a valid describe request,
		does not mean the container exists or other errors are impossible """
	def __init__(self, db_req):
		self.container_name:str = None

		self.getContainterName(db_req)

	def getContainterName(self, db_req):
		self.container_name = db_req.get("name", "")
		if type(self.container_name) is not str:
			self.container_name = str(self.container_name)

		self.container_name = self.container_name.replace('..', '')
		self.container_name = self.container_name.strip('/')

		if not self.container_name: raise MissingNameField()

async def describe(self, request):
	""" Used to get the defaults value list of a container, pretty much the counterpart to self.default """


async def performDescribe(db_instance, describe_request):

	container = await db_instance.load(describe_request.container_name)

	if container.status == "sys_error": raise SysLoadError(describe_request.container_name)
	elif container.status == "not_found": raise ContainerNotFound(describe_request.container_name)
	elif container.status == "success":	container = container.content

	default_template = container.get("default", dict())

	#awnser
	res = dict(
		code=200,
		status="described",
		container=describe_request.container_name,
		default=default_template,
		msg=f"described container '{describe_request.container_name}'"
	)

	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"described container '{describe_request.container_name}'")
	return db_instance.response(status=200, body=json.dumps(res))

class EmptyObject(): pass
