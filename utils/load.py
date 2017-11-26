import pickle, os

def load(container_name, DUMP):
	if not os.path.isfile("DATABASE/{}.phaazedb".format(container_name)):
		return None

	file_path = "DATABASE/{}.phaazedb".format(container_name)
	container = pickle.load(open(file_path, "rb"))

	#store in Dump
	DUMP[container_name] = container

	return container