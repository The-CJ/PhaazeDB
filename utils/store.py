import pickle, threading, os
from utils.container import Container

lock = threading.Lock()
locked_files = []

async def store(self, container_name, container_content, create=False, ignore_save_limit=False):

	# get container info object from db, based on name, won't be avariable if new container must be created
	container = self.db.get(container_name, None)
	if container == None:
		container = Container(self, container_name)

	container.actions_since_save += 1

	if not container.actions_since_save > self.save_interval and not ignore_save_limit:
		# continue without saving
		return True

	success = await performStore(self, container_name, container_content, create)
	# save successfull, reset save counter
	if success: container.actions_since_save = 0
	return success

async def performStore(db_instance, container_name, container_content, create):

	container_path = f"{db_instance.container_root}{container_name}.phaazedb"

	# is a new container, check for subfolder and create
	if create:
		os.makedirs(os.path.dirname(container_path), exist_ok=True)

	# its not in create mode, but its trying to save to this file, return False
	if not os.path.isfile(container_path) and not create:
		return False

	# file is already open -> wait until lock opened -> lock it + add name
	if container_name in locked_files:
		lock.acquire()
		locked_files.append(container_name)
	# file is not opened -> lock without time delay + add name
	else:
		lock.acquire()
		locked_files.append(container_name)

	pickle.dump(container_content, open(container_path, "wb") )

	#operation finished -> remove name + release Lock
	locked_files.remove(container_name)
	lock.release()

	return True
