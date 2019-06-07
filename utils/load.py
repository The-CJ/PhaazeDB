from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import asyncio
import pickle, os
from utils.container import Container

async def load(cls:"PhaazeDatabase", container_name:str, only_already_loaded:bool=False):

	AlreadyLoadedContainer:Container = cls.db.get(container_name, None)
	if AlreadyLoadedContainer != None:
		# reset time
		AlreadyLoadedContainer.keep_alive_time_left = cls.keep_alive
		return AlreadyLoadedContainer

	# its not currently loaded in ram, don't load it, just give None back
	if only_already_loaded: return None

	#try to load
	container_location:str = f"{cls.container_root}{container_name}.phaazedb"

	#does not exist
	if not os.path.isfile(container_location):
		return Container(cls, container_name, status="not_found")

	try:
		container_content:dict = pickle.load(open(container_location, "rb"))
		#store in db, for X time -> unload from RAM
		cls.db[container_name] = Container(cls, container_name, status="success", content=container_content, keep_alive=cls.keep_alive)
		asyncio.ensure_future(cls.db[container_name].countDown())
		return cls.db[container_name]

	except Exception as e:
		cls.PhaazeDBS.Logger.error(f"Error loading container '{container_name}': {str(e)}")
		return Container(cls, container_name, status="sys_error")
