import os, pickle, json
from datetime import datetime
from utils.errors import MissingNameField, ContainerAlreadyExists

class CreateRequest(object):
	""" Contains informations for a valid create request,
		does not mean the container may not already be existing or other errors are iompossible """
	def __init__(self, db_req):
		self.container_name:str = None

		self.getContainterName(db_req)

	def getContainterName(self, db_req):
		self.container_name = db_req.get("name", "")
		self.container_name = self.container_name.replace('..', '')
		self.container_name = self.container_name.strip('/')

		if not self.container_name: raise MissingNameField()

async def create(self, request):
	""" Used to create new container in the database (automaticly creates supercontainer if necessary) """

	# prepare request for a valid search
	try:
		create_request = CreateRequest(request.db_request)
		return await performCreate(self, create_request)

	except (MissingNameField, ContainerAlreadyExists) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

async def performCreate(db_instance, create_request):
	container_location = f"{db_instance.container_root}{create_request.container_name}.phaazedb"

	#already exist
	if os.path.isfile(container_location):
		raise ContainerAlreadyExists(create_request.container_name)

	container = dict (
		current_id = 1,
		data = dict(),
		default = dict(),
		creation_date = str(datetime.now())
	)

	try:
		#add file folders
		os.makedirs(os.path.dirname(file_path), exist_ok=True)

		#add file
		pickle.dump(container, open(file_path, "wb") )

		#add to active db
		self.db[table_name] = container

		#awnser
		res = dict(
			code=201,
			status="created",
			msg=f"created container '{table_name}'"
		)
		if self.log != False:
			self.logger.info(f"created container '{table_name}'")
		return self.response(status=201, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		if self.log != False:
			self.logger.critical(f"create container '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))

