from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import asyncio

class Container(object):
	"""
		Represents a containter from the db, actuall data is in self.content
		all other functions are for internal managment
	"""
	def __init__(self, Database:"PhaazeDatabase", name:str, status:str="sys_error", content=dict(), keep_alive:int=0):
		self.Database:"PhaazeDatabase" = Database
		self.name:str = name
		self.status:str = status
		self.content:dict = content

		self.keep_alive_time_left:int = keep_alive
		self.actions_since_save:int = 0
		self.removed:bool = False

	@property
	def default(self) -> dict:
		return self.content.get("default", dict())

	@property
	def data(self) -> list:
		return self.content.get("data", list())

	@property
	def currentid(self) -> int:
		return self.content.get("current_id", 0)

	async def countDown(self) -> bool:
		"""
			counts down the keep alive counter, if end -> save to file, unload from ram
			must be start called from outside, most likly Database.load()
		"""
		while self.keep_alive_time_left > 0:
			self.keep_alive_time_left -= 1
			await asyncio.sleep(1)

		return await self.remove()

	async def remove(self, remove_from_ram:bool=True, store:bool=True) -> bool:
		"""
			Removes a container from RAM and saves it to file system
			get called by self.countDown automaticly or from manual store or else.
		"""
		if self.removed:
			return True
		self.removed = True
		self.keep_alive_time_left = 0

		# save content
		success:bool = await self.Database.store(self.name, self.content, ignore_save_limit=True) if store else True
		if not success:
			self.Database.Server.Logger.critical(f"Could not store: '{self.name}' before unloading")
			return False

		# delete from ram
		if remove_from_ram: del self.Database.db[self.name]
		return True

	async def save(self) -> bool:
		"""
			Short for: self.remove(remove_from_ram=False)
			Does not remove a container from RAM but saves it to file system.
		"""
		return await self.remove(remove_from_ram=False)

	async def delete(self) -> bool:
		"""
			Short for: self.remove(remove_from_ram=True, store=False)
			Removes a container from RAM and does NOT saves it to file system.
		"""
		return await self.remove(remove_from_ram=True, store=False)
