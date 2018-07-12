import pickle, threading, os


lock = threading.Lock()
locked_files = []

async def store(self, container_name, container_content):

	if not os.path.isfile(f"DATABASE/{container_name}.phaazedb"):
		return False

	#file is already open -> wait until lock opened -> lock it + add name
	if container_name in locked_files:
		lock.acquire()
		locked_files.append(container_name)
	#file is not opened -> lock without time delay + add name
	else:
		lock.acquire()
		locked_files.append(container_name)

	pickle.dump(container_content, open(f"DATABASE/{container_name}.phaazedb", "wb") )

	#operation finished -> remove name + release Lock
	locked_files.remove(container_name)
	lock.release()

	return True
