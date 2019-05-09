import asyncio

class Container(object):
	""" Represents a containter from the db, actuall data is in self.content
		all other functions are for internal menagment """
	def __init__(self, db_instance, name, status="sys_error", content=None, keep_alive=0):
		self.db_instance = db_instance
		self.name = name
		self.status = status
		self.content = content

		self.keep_alive_time_left = keep_alive
		self.actions_since_save = 0
		self.removed = False

	async def countDown(self):
		""" counts down the keep alive counter, if end -> save to file, unload from ram
			must be start called from outside, most likly DB.load() """
		while self.keep_alive_time_left > 0:
			self.keep_alive_time_left -= 1
			await asyncio.sleep(1)

		return await self.remove()

	async def remove(self):
		if self.removed: return True
		self.removed = True
		self.keep_alive_time_left = 0

		# save content
		success = await self.db_instance.store(self.name, self.content)
		if not success:
			self.db_instance.Server.Logger.critical(f"Could not store: '{self.name}' before unloading")
			return False

		# delete from ram
		del self.db_instance.db[self.name]
		return True

