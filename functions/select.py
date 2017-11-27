import json

from utils.load import load as load

class not_found():
	"Dummy class"

def check_data_if_needed(data, where):
	if where == []:
		return True

	valid = True
	for statement in where:
		if len(statement) == 0:
			valid = False
			continue

		if statement[0] in [1, True]:
			continue

		if len(statement) == 1:
			check = data.get(statement[0], not_found)
			if check == not_found:
				valid = False
				continue
			else: continue

		key = statement[0]
		compare = statement[1]
		value = statement[2]

		if not compare in ["==", "!=", "in", "not in", ">", "<", ">=" ,"<=", "<>"]:
			valid = False

		key_in_db = data.get(key, None)

		check_str = '{0} {1} {2}'.format(key_in_db, compare, value)
		try:
			state = eval(check_str)
		except:
			state = False

		if state:
			pass
		else:
			valid = False


	return valid

def requested_data(data, requested_fields):
	if requested_fields == []:
		return data

	d = {}
	for field in requested_fields:
		x = data.get(field, None)
		d[field] = x

	return d

def select(content, DUMP):
	table_name = content.get("from", None)
	requested_fields = content.get("fields", [])
	where = content.get("where", [])

	#error handling

	#no name
	if table_name == None:
		class r():
			response = 400
			content = b'{"error":"field: `from` missing"}'
		return r

	already_loaded = DUMP.get(table_name, None)
	if already_loaded == None:
		#not loaded -> load in
		active_container = load(table_name, DUMP)

	else:
		active_container = already_loaded

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
		content = str(dict(
		hits=len(return_data),
		data=return_data
		)).encode("UTF-8")
	return r
