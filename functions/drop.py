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

async def drop(self, request, _INFO):
	""" Used to drop/delete container from DB (automaticly deletes supercontainer if necessary) """

	#get required vars (POST -> JSON based)

	#no tabel name
	table_name = _INFO.get('_POST', {}).get('name', "")
	if table_name == "":
		table_name = _INFO.get('_JSON', {}).get('name', "")

	if type(table_name) is not str:
		table_name = str(table_name)

	table_name = table_name.replace('..', '')
	table_name = table_name.strip('/')

	#no name
	if table_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'name' field"
		)
		return self.response(status=400, body=json.dumps(res))

	#does not exist
	if not os.path.isfile(f"DATABASE/{table_name}.phaazedb"):
		res = dict(
			code=400,
			status="error",
			msg=f"container '{table_name}' does not exist"
		)
		return self.response(status=400, body=json.dumps(res))

	file_path = f"DATABASE/{table_name}.phaazedb"

	try:
		#remove from file system
		os.remove(file_path)

		#remove from active db
		self.db.pop(table_name, None)

		#remove upper folder
		drop_upper_empty_folder(table_name)

		res = dict(
			code=200,
			status="droped",
			msg=f"droped container '{table_name}'"
		)
		if self.log != False:
			self.logger.info(f"droped container '{table_name}'")
		return self.response(status=200, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		if self.log != False:
			self.logger.critical(f"drop container '{table_name}' failed")
		return self.response(status=500, body=json.dumps(res))