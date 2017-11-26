import pickle, threading, os

lock = threading.Lock()

locked_files = []

def store(name, file_content):

	if not os.path.isfile("DATABASE/{}.phaazedb".format(name)):
		return False

	#file is already open -> wait until lock opened -> lock it + add name
	if name in locked_files:
		lock.acquire()
		locked_files.append(name)
	#file is not opened -> lock without time delay + add name
	else:
		lock.acquire()
		locked_files.append(name)

	pickle.dump(file_content, open("DATABASE/{}.phaazedb".format(name), "wb") )

	#operation finished -> remove name + release Lock
	locked_files.remove(name)
	lock.release()

	return True
