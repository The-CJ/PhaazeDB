import json, os

from utils.load import load as load

def get_folder_content(p):
	r = {'supercontainer': {},'container': []}
	for thing in os.listdir('DATABASE/'+p):
		if thing.endswith('.phaazedb'):
			thing = thing.split('.phaazedb')[0]
			r['container'].append(thing)

		else:
			r['supercontainer'][thing] = get_folder_content(p+"/"+thing)

	return r

def show(content, DUMP):

	all_container = {'supercontainer': {},'container': []}

	for thing in os.listdir('DATABASE'):
		if thing.endswith('.phaazedb'):
			thing = thing.split('.phaazedb')[0]
			all_container['container'].append(thing)

		else:
			all_container['supercontainer'][thing] = get_folder_content(thing)


	class r():
		response = 200
		content = str(
			json.dumps(
				dict(
					status="showed",
					data=all_container
					)
				)
			).encode("UTF-8")
	return r
