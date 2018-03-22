import json, math

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

	#get request limit and offset
	offset = content.get("offset", 0)
	if type(offset) is not int:
		try:
			offset = int(offset)
		except:
			offset = 0
	limit = content.get("limit", math.inf)
	if type(limit) is not int:
		try:
			limit = int(limit)
		except:
			limit = math.inf

	hits = 0
	field_count = 0
	cur_offset = 0

	for data in active_container.get("data", []):
		#check if data is needed -> check where
		try:
			v = check_data_if_needed(data, where)
		except:
			v = False

		if not v:
			continue

		cur_offset += 1

		if offset >= cur_offset: continue
		hits += 1
		actuall_requested_data = requested_data(data, requested_fields)
		field_count = field_count + len(actuall_requested_data)
		return_data.append(actuall_requested_data)

		if hits >= limit:
			break

	class r():
		response = 200
		content = str(
			json.dumps(
				dict(
					status="selected",
					hits=hits,
					hits_field=field_count,
					total=len(active_container.get("data", [])),
					data=return_data
					)
				)
			).encode("UTF-8")
	return r
