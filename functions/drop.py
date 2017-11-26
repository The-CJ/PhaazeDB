import os

def drop(content):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 406
			content = b'{"error":"field: `name` missing"}'
		return r

	if not os.path.isfile("DATABASE/{}.phaazedb".format(table_name)):
		class r():
			response = 405
			content = '{"error":"container `{tbn}` does not exists"}'.replace('{tbn}', table_name).encode("UTF-8")
		return r

	#everything ok, del db

	path = "DATABASE/{}.phaazedb".format(table_name)

	os.remove(path)

	class r():
		response = 202
		content = b'{"msg":"successfull deleted"}'
	return r
