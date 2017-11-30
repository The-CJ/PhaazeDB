import os, pickle, json
from datetime import datetime

def create(content):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `name` missing",
					name=table_name
				)
			).encode("UTF-8")
		return r

	if os.path.isfile("DATABASE/{}.phaazedb".format(table_name)):
		class r():
			response = 405
			content = json.dumps(
				dict(
					status="error",
					msg="container already exist",
					name=table_name
				)
			).encode("UTF-8")
		return r

	#everything ok, make db

	container = dict (
		current_id = 1,
		data = [],
		creation_date = str(datetime.now())
	)

	g = "DATABASE/{}.phaazedb".format(table_name)
	g = g.replace("../", "")

	os.makedirs(os.path.dirname(g),exist_ok=True)

	pickle.dump(container, open(g, "wb") )

	class r():
		response = 201
		content = json.dumps(
			dict(
				status="created",
				msg="container created",
				name=table_name
			)
		).encode("UTF-8")
	return r
