import asyncio, json, os

async def show(self, request, _INFO):
	""" Shows container hierarchy from 'name' or all if not defined """

	#get recursive path
	recursive = _INFO.get('_GET', {}).get('recursive', None)
	if recursive == None:
		recursive = _INFO.get('_JSON', {}).get('recursive', None)
	if recursive == None:
		recursive = _INFO.get('_POST', {}).get('recursive', None)

	if type(recursive) is not bool:
		recursive = bool(recursive)

	#get show path
	path = _INFO.get('_GET', {}).get('path', None)
	if path == None:
		path = _INFO.get('_JSON', {}).get('path', None)
	if path == None:
		path = _INFO.get('_POST', {}).get('path', None)

	if path == None:
		path = ""
	else:
		path = str(path)

	path = path.replace('..', '')
	path = path.strip('/')
	path = "DATABASE/"+path

	###

	#check if there
	try:
		os.listdir(path)
	except Exception as e:
		res = dict(
			code=400,
			status="error",
			msg=f"no tree path found at '{path}'",
		)
		return self.response(status=400, body=json.dumps(res))

	root = {'supercontainer': {},'container': []}

	tree = await get_container(root, path, recursive=recursive)

	###

	res = dict(
		code=200,
		status="showed",
		path=path,
		recursive=recursive,
		tree=tree
	)
	if self.log != False:
		self.log.info(f"showed tree: path={path}, recursive={str(recursive)}")
	return self.response(status=200, body=json.dumps(res))

async def get_container(tree, folder_path, recursive=False):
	for file in os.listdir(folder_path):

		#is container
		if file.endswith('.phaazedb'):
			file = file.split('.phaazedb')[0]
			tree['container'].append(file)

		#is supercontainer
		else:
			if recursive:
				tree['supercontainer'][file] = await get_container(dict(supercontainer={}, container=[]), folder_path + "/" + file)
			else:
				tree['supercontainer'][file] = {}

	return tree
