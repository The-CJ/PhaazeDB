import os, pickle
from datetime import datetime

def create(content):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 406
			content = b'{"error":"field: `name` missing"}'
		return r

	if os.path.isfile("DATABASE/{}.phaazedb".format(table_name)):
		class r():
			response = 405
			content = '{"error":"container `{tbn}` already exists"}'.replace('{tbn}', table_name).encode("UTF-8")
		return r

	#everything ok, make db

	container = dict (
		current_id = 1,
		data = [],
		creation_date = str(datetime.now())
	)

	pickle.dump(container, open("DATABASE/{}.phaazedb".format(table_name), "wb") )

	class r():
		response = 201
		content = b'{"msg":"successfull created"}'
	return r
