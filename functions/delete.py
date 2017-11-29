from utils.load import load
from utils.store import store

import json

def check_data_if_needed(data, where):
	if where == "":
		return True

	if eval(where):
		return True

	return False



def delete(content, DUMP):
	table_name = content.get("of", None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `of` missing"
				)
			).encode("UTF-8")

		return r

	already_loaded = DUMP.get(table_name, None)
	if already_loaded == None:
		#not loaded -> load in
		active_container = load(table_name, DUMP)

	else:
		active_container = already_loaded

	if active_container == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="container dont\' exist",
					name=table_name
				)
			).encode("UTF-8")
		return r

	where = content.get("where", "")

	hit = 0
	new_db = []

	for data in active_container.get("data", []):
		#check if data is needed -> check where
		try:
			v = check_data_if_needed(data, where)
		except:
			v = False

		if not v:
			new_db.append(data)
		else: hit += 1

	active_container["data"] = new_db

	s = store(table_name, active_container)

	if s:
		class r():
			response = 201
			content = json.dumps(
				dict(
					status="deleted",
					msg="data successfull deleted",
					container=table_name,
					hits=hit
				)
			).encode("UTF-8")
		return r
	else:
		class r():
			response = 500
			content = json.dumps(
				dict(
					status="error",
					msg="unknown server error"
				)
			).encode("UTF-8")
		return r
