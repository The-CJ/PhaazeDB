import os, pickle, json
from datetime import datetime

async def create(self, request, _INFO):
	""" Used to create new container in the database (automaticly creates supercontainer if necessary) """

	#get reqired vars (POST -> JSON based)

	#no tabel name
	table_name = _INFO.get('_POST', {}).get('name', "")
	if table_name == "":
		table_name = _INFO.get('_JSON', {}).get('name', "")

	if type(table_name) is not str:
		table_name = str(table_name)

	table_name = table_name.replace('..', '')
	table_name = table_name.strip('/')

	if table_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'name' field"
		)
		return self.response(status=400, body=json.dumps(res))

	#already exist
	if os.path.isfile(f"DATABASE/{table_name}.phaazedb"):
		res = dict(
			code=400,
			status="error",
			msg=f"container '{table_name}' already exist"
		)
		return self.response(status=400, body=json.dumps(res))

	container = dict (
		current_id = 1,
		data = dict(),
		creation_date = str(datetime.now())
	)

	file_path = f"DATABASE/{table_name}.phaazedb"

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
		return self.response(status=201, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		return self.response(status=500, body=json.dumps(res))
