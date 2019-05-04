import os, json
from datetime import datetime
from utils.errors import MissingNameField, ContainerAlreadyExists, SysCreateError

class CreateRequest(object):
	""" Contains informations for a valid create request,
		does not mean the container may not already be existing or other errors are impossible """
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

async def create(self, request):
	""" Used to create new container in the database (automaticly creates supercontainer if necessary) """

	# prepare request for a valid search
	try:
		create_request = CreateRequest(request.db_request)
		return await performCreate(self, create_request)

	except (MissingNameField, ContainerAlreadyExists, SysCreateError) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performCreate(db_instance, create_request):
	container_location = f"{db_instance.container_root}{create_request.container_name}.phaazedb"

	#already exist
	if os.path.isfile(container_location):
		raise ContainerAlreadyExists(create_request.container_name)

	success = await makeNewContainer(db_instance, create_request.container_name)

	if not success:
		db_instance.Server.Logger.critical(f"create container '{create_request.container_name}' failed")
		raise SysCreateError(create_request.container_name)

	res = dict(
		code=201,
		status="created",

		msg=f"created container '{create_request.container_name}'"
	)
	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"created container '{create_request.container_name}'")
	return db_instance.response(status=201, body=json.dumps(res))

async def makeNewContainer(db_instance, container_name):
	new_container = dict (
		current_id = 1,
		data = dict(),
		default = dict(),
		creation_date = str(datetime.now())
	)

	created = await db_instance.store(container_name, new_container, create=True)

	return created, new_container
