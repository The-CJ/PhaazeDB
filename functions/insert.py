from utils.load import load
from utils.store import store

import json

def insert(content, DUMP):
	table_name = content.get("into", None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `into` missing"
				)
			).encode("UTF-8")

		return r

	content_to_add = content.get("content", None)
	if content_to_add == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `content` missing"
				)
			).encode("UTF-8")
		return r

	content_to_add.pop('id', None)

	if content_to_add in [{}, [], "", 0] or not type(content_to_add) is dict:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					msg="field: `content` is missing a usable JSON {key: value} value"
				)
			).encode("UTF-8")
		return r

	if content_to_add.get('', "4458216asd1qrqw12a12aycac211qewefebgr225wgre545") != "4458216asd1qrqw12a12aycac211qewefebgr225wgre545":
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
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

	#add id value
	content_to_add["id"] = active_container['current_id']

	active_container["data"].append(content_to_add)
	active_container["current_id"] += 1

	s = store(table_name, active_container)

	if s:
		class r():
			response = 201
			content = json.dumps(
				dict(
					status="inserted",
					msg="data successfull added",
					container=table_name,
					content=content_to_add
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
