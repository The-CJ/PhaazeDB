import asyncio

import pickle, os

class db_obj(object):
	def __init__(self, status="sys_error", content=None):
		self.status = status
		self.content = content

async def load(self, container_name):

	existing_container = self.db.get(container_name, None)

	#try to load
	container_location = f"DATABASE/{container_name}.phaazedb"
	if existing_container == None:
		#does not exist
		if not os.path.isfile(container_location):
			return db_obj(status="not_found")

	try:
		container = pickle.load(open(container_location, "rb"))
		#store in db
		self.db[container_name] = container
		return db_obj(status="success", content=container)

	except:
		return db_obj(status="sys_error")

