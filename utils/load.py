import asyncio

import pickle, os

class Container(object):
	def __init__(self, db_instance, name, status="sys_error", content=None, keep_alive=0):
		self.db_instance = db_instance
		self.name = name
		self.keep_alive_time_left = keep_alive
		self.status = status
		self.content = content

	async def countDown(self):
		while self.keep_alive_time_left > 0:
			self.keep_alive_time_left -= 1
			await asyncio.sleep(1)

		del self.db_instance.db[self.name]

async def load(self, container_name):

	already_loaded = self.db.get(container_name, None)
	if already_loaded != None:
		# reset time
		already_loaded.keep_alive_time_left = self.keep_alive
		return already_loaded

	#try to load
	container_location = f"{self.container_root}{container_name}.phaazedb"

	#does not exist
	if not os.path.isfile(container_location):
		return Container(self, container_name, status="not_found")

	try:
		container = pickle.load(open(container_location, "rb"))
		#store in db, for X time -> unload from RAM
		self.db[container_name] = Container(self, container_name, status="success", content=container, keep_alive=self.keep_alive)
		asyncio.ensure_future(self.db[container_name].countDown())
		return self.db[container_name]

	except Exception as e:
		self.Server.Logger.error(f"Error loading container '{container_name}': {str(e)}")
		return Container(self, container_name, status="sys_error")
