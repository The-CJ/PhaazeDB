import os, pickle, json
from datetime import datetime

def create(content):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					code=400,
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
					code=405,
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

	try:
		os.makedirs(os.path.dirname(g),exist_ok=True)

		pickle.dump(container, open(g, "wb") )

	except:
		class r():
			response = 500
			content = json.dumps(
				dict(
					code=500,
					status="error",
					msg="unknown server error"
				)
			).encode("UTF-8")
		return r

	class r():
		response = 201
		content = json.dumps(
			dict(
				code=201,
				status="created",
				msg="container created",
				name=table_name
			)
		).encode("UTF-8")
	return r
