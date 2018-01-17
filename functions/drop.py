import os, json

def drop(content):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `name` missing"
				)
			).encode("UTF-8")

		return r

	if not os.path.isfile("DATABASE/{}.phaazedb".format(table_name)):
		class r():
			response = 405
			content = json.dumps(
				dict(
					status="error",
					msg="container does not exists",
					name=table_name
				)
			).encode("UTF-8")

		return r

	path = "DATABASE/{}.phaazedb".format(table_name)

	os.remove(path)

	class r():
		response = 202
		content = json.dumps(
			dict(
				status="droped",
				msg="container successfull droped",
				name=table_name
			)
		).encode("UTF-8")

	return r
