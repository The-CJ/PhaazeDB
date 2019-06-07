from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import pickle, threading, os
from utils.container import Container

Lock:threading.Lock = threading.Lock()
locked_files:list = []

async def store(cls:"PhaazeDatabase", DBContainer:Container, create:bool=False, ignore_save_limit:bool=False) -> bool:

	DBContainer.actions_since_save += 1

	# one condtion = save
	if (DBContainer.actions_since_save > cls.save_interval and cls.save_interval > -1) or ignore_save_limit or create:
		success = await performStore(cls, DBContainer, create)
		# save successfull, reset save counter
		if success: DBContainer.actions_since_save = 0
		return success
	else:
		return True

async def performStore(cls:"PhaazeDatabase", DBContainer:Container, create:bool):

	container_path:str = f"{cls.container_root}{DBContainer.name}.phaazedb"

	# is a new container, check for subfolder and create
	if create:
		os.makedirs(os.path.dirname(container_path), exist_ok=True)

	# its not in create mode, but its trying to save to this file, return False
	if not os.path.isfile(container_path) and not create:
		return False

	# file is already open -> wait until lock opened -> lock it + add name
	if DBContainer.name in locked_files:
		Lock.acquire()
		locked_files.append(DBContainer.name)
	# file is not opened -> lock without time delay + add name
	else:
		Lock.acquire()
		locked_files.append(DBContainer.name)

	try:
		pickle.dump(DBContainer.content, open(container_path, "wb") )
		state:bool = True

	except Exception as e:
		cls.PhaazeDBS.Logger.critical("Pickel failed while storing container: " + str(e))
		state:bool = False

	finally:
		#operation finished -> remove name + release Lock
		locked_files.remove(DBContainer.name)
		Lock.release()
		return state
