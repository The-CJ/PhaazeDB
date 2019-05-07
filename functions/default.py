import json
from utils.errors import MissingNameField, InvalidContent, SysLoadError, ContainerNotFound, SysStoreError

class DefaultRequest(object):
	""" Contains informations for a valid container default request,
		does not mean the container may not already be existing or other errors are impossible """
	def __init__(self, db_req):
		self.container_name:str = None
		self.default_content:dict = None

		self.getContainterName(db_req)
		self.getContainterTemplate(db_req)

	def getContainterName(self, db_req):
		self.container_name = db_req.get("name", "")
		if type(self.container_name) is not str:
			self.container_name = str(self.container_name)

		self.container_name = self.container_name.replace('..', '')
		self.container_name = self.container_name.strip('/')

		if not self.container_name: raise MissingNameField()

	def getContainterTemplate(self, db_req):
		self.default_content = db_req.get("content", "")

		if type(self.default_content) is str:
			try:
				self.default_content = json.loads(self.default_content)
			except:
				raise InvalidContent()

		if type(self.default_content) is not dict:
			raise InvalidContent()

async def default(self, request):
	"""
		Used to set a new object as default for a container,
		values in default set always get added to a select request, (if requested in 'fields')
		so values will always be there
	"""

	# prepare request for a valid search
	try:
		default_request = DefaultRequest(request.db_request)
		return await performDefault(self, default_request)

	except (MissingNameField) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performDefault(db_instance, default_request):

	#unnamed key
	if default_request.content.get('', EmptyObject) != EmptyObject:
		raise InvalidContent(True)

	container = await db_instance.load(default_request.container_name)

	if container.status == "sys_error": raise SysLoadError(default_request.container_name)
	elif container.status == "not_found": raise ContainerNotFound(default_request.container_name)
	elif container.status == "success":	container = container.content

	# actully set it
	container["default"] = default_request.default_content

	#save everything
	success = await default_request.store(default_request, container)

	if not success:
		db_instance.Server.Logger.critical(f"setting default set for container '{default_request.container_name}' failed")
		raise SysStoreError(default_request.container_name)

	res = dict(
		code=200,
		status="default set",
		container=default_request.container_name,
		default=default_request.default_content,
		msg=f"default set for container '{default_request.container_name}'"
	)
	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"default set for container '{default_request.container_name}'")
	return db_instance.response(status=200, body=json.dumps(res))

class EmptyObject(): pass