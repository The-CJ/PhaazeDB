import json

from utils.load import load as load

class not_found():
	"Dummy class"

def check_data_if_needed(data, where):
	if where == "":
		return True

	if eval(where):
		return True

	return False

def requested_data(data, requested_fields):
	if requested_fields == []:
		return data

	d = {}
	for field in requested_fields:
		x = data.get(field, None)
		d[field] = x

	return d

def select(content, DUMP):
	table_name = content.get("of", None)
	requested_fields = content.get("fields", [])
	where = content.get("where", "")

	#error handling

	#no name
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `of` missing",
				)
			).encode("UTF-8")
		return r

	already_loaded = DUMP.get(table_name, None)
	if already_loaded == None:
		#not loaded -> load in
		active_container = load(table_name, DUMP)

	else:
		active_container = already_loaded


	#no container found
	if active_container == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="container don\'t exist",
					name=table_name
				)
			).encode("UTF-8")
		return r

	return_data = []

	for data in active_container.get("data", []):
		#check if data is needed -> check where
		try:
			v = check_data_if_needed(data, where)
		except:
			v = False

		if not v:
			continue

		actuall_requested_data = requested_data(data, requested_fields)
		return_data.append(actuall_requested_data)

	class r():
		response = 200
		content = str(
			json.dumps(
				dict(
					hits=len(return_data),
					data=return_data
					)
				)
			).encode("UTF-8")
	return r
