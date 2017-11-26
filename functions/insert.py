from utils.load import load
from utils.store import store

def insert(content, DUMP):
	table_name = content.get("from", None)
	if table_name == None:
		class r():
			response = 400
			content = b'{"error":"field: `from` missing"}'
		return r

	content_to_add = content.get("content", None)
	if content_to_add == None:
		class r():
			response = 400
			content = b'{"error":"field: `content` missing"}'
		return r

	if content_to_add in [{}, [], "", 0] or not type(content_to_add) is dict:
		class r():
			response = 400
			content = b'{"error":"field: `content` is missing a usable value", "msg":"please send at least a simple JSON: {key: value} as `content`"}'
		return r

	already_loaded = DUMP.get(table_name, None)
	if already_loaded == None:
		#not loaded -> load in
		active_container = load(table_name, DUMP)

	else:
		active_container = already_loaded

	#add id value
	content_to_add["id"] = active_container['current_id']

	active_container["data"].append(content_to_add)
	active_container["current_id"] += 1

	s = store(table_name, active_container)

	if s:
		class r():
			response = 201
			content = '{"msg":"successfull added", "content":{con}}'.replace('{con}', str(content_to_add)).encode("UTF-8")
		return r
	else:
		class r():
			response = 500
			content = b'{"error":"entry could not be entered"}'
		return r
