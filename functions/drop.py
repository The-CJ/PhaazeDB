import os, json
from utils.errors import MissingNameField, ContainerNotFound

class DropRequest(object):
	""" Contains informations for a valid drop request,
		does not mean the container must exist or other errors are impossible """
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

async def drop(self, request):
	""" Used to drop/delete container from DB and delete supercontainer if no container are left """

	# prepare request for a valid search
	try:
		drop_request = DropRequest(request.db_request)
		return await performDrop(self, drop_request)

	except (MissingNameField, ContainerNotFound) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performDrop(db_instance, drop_request):
	""" Used to drop/delete container from DB (automaticly deletes supercontainer if necessary) """

	container_location = f"{db_instance.container_root}{drop_request.container_name}.phaazedb"

	#does not exist
	if not os.path.isfile(container_location):
		raise ContainerNotFound(drop_request.container_name)

	#remove from file system
	os.remove(container_location)

	#remove from active db
	currently_loaded = await db_instance.load(drop_request.container_name, only_already_loaded=True)
	if currently_loaded:
		await currently_loaded.delete()

	#remove upper folder if empty
	await DropSupercontainer(db_instance, drop_request.container_name)

	res = dict(
		code=200,
		status="droped",
		msg=f"droped container '{drop_request.container_name}'"
	)

	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"droped container '{drop_request.container_name}'")
	return db_instance.response(status=200, body=json.dumps(res))

async def DropSupercontainer(db_instance, container_name):

	supercontainer_path = os.path.dirname(container_name)
	c = os.listdir(f"{db_instance.container_root}{supercontainer_path}")

	#folder is now empty -> remove
	if len(c) == 0:
		# ignore database root dir
		if supercontainer_path == "": return

		os.rmdir(f"{db_instance.container_root}{supercontainer_path}")

		#check if the supercontainer of this is is now empty as well
		await DropSupercontainer(db_instance, supercontainer_path)