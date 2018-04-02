import json

from utils.load import load as load
from utils.store import store

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

def update(content, DUMP):
	table_name = content.get("of", None)
	where = content.get("where", "")

	#error handling
	#no content
	content_to_update = content.get("content", None)
	if content_to_update == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					code=400,
					msg="field: `content` missing"
				)
			).encode("UTF-8")
		return r

	content_to_update.pop('id', None)

	if content_to_update in [{}, [], "", 0] or not type(content_to_update) is dict:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					code=400,
					msg="field: `content` is missing a usable JSON {key: value} value"
				)
			).encode("UTF-8")
		return r

	#no name
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					code=400,
					msg="field: `of` missing",
				)
			).encode("UTF-8")
		return r

	if content_to_update.get('', None) != None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					code=400,
					msg="field: `content` has a unnamed JSON key"
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
					code=400,
					msg="container don\'t exist",
					name=table_name
				)
			).encode("UTF-8")
		return r

	return_data = []
	hits=0

	for data in active_container.get("data", []):
		#check if data is needed -> check where
		try:
			v = check_data_if_needed(data, where)
		except:
			v = False

		if v:
			hits += 1
			for key in content_to_update:
				if key == "id":
					continue

				data[key] = content_to_update[key]

				if content_to_update[key] == "<!<-rf->!>":
					data.pop(key, None)


		return_data.append(data)

	s = store(table_name, active_container)

	if s:
		class r():
			response = 200
			content = json.dumps(dict(
				status="updated",
				code=200,
				hits=hits,
				msg="successfull updated/added values"
			)).encode("UTF-8")
		return r
	else:
		class r():
			response = 500
			content = json.dumps(
				dict(
					status="error",
					code=500,
					msg="unknown server error"
				)
			).encode("UTF-8")
		return r

