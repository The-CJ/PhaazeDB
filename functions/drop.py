import os, json

def drop_upper_empty_folder(table_name):

	t = [r for r in table_name.split('/')]
	t.pop()
	t = "/".join(f for f in t)
	c = os.listdir("DATABASE/{}".format(t))

	#folder is now empty -> remove
	if len(c) == 0:
		if t == "": return

		os.rmdir("DATABASE/{}".format(t))

		#check if this is now empty as well
		drop_upper_empty_folder(t)


def drop(content, DUMP):
	table_name = content.get('name', None)
	if table_name == None:
		class r():
			response = 400
			content = json.dumps(
				dict(
					status="error",
					code=400,
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
					code=405,
					msg="container does not exists",
					name=table_name
				)
			).encode("UTF-8")

		return r

	path = "DATABASE/{}.phaazedb".format(table_name)

	os.remove(path)
	DUMP.pop(table_name, None)

	try:
		drop_upper_empty_folder(table_name)
	except:
		pass

	class r():
		response = 202
		content = json.dumps(
			dict(
				status="droped",
				code=202,
				msg="container successfull droped",
				name=table_name
			)
		).encode("UTF-8")

	return r
