import os, json

import asyncio

def drop_upper_empty_folder(table_name):

	t = [r for r in table_name.split('/')]
	t.pop()
	t = "/".join(f for f in t)
	c = os.listdir("DATABASE/{}".format(t))

	#folder is now empty -> remove
	if len(c) == 0:
		if t == "": return

		os.rmdir("DATABASE/{}".format(t))

		#check if this is now empty as well
		drop_upper_empty_folder(t)

async def drop(self, request, _INFO):
	""" Used to drop/delete container from DB (automaticly deletes supercontainer if necessary) """

	#get reqired vars (POST -> JSON based)

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
		return self.response(status=200, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		return self.response(status=500, body=json.dumps(res))
