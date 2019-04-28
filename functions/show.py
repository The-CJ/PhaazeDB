import asyncio, json, os

class ShowRequest(object):
	""" Contains informations for a valid show request,
		does not mean if can be executed without errors """
	def __init__(self, db_req):
		self.recursive:bool = False
		self.path:str = None

		self.getRecursive(db_req)
		self.getPath(db_req)

	def getRecursive(self, db_req):
		self.recursive = db_req.get("recursive",None)
		if type(self.recursive) is not bool:
			self.recursive = bool(self.recursive)

	def getPath(self, db_req):
		self.path = db_req.get("path", "")
		if type(self.path) is not str:
			self.path = str(self.path)

		self.path = self.path.replace('..', '')
		self.path = self.path.strip('/')

		if not self.path: self.path = ""

async def show(self, request):
	""" Shows container hierarchy from 'name' or all if not defined """

	try:
		show_request = ShowRequest(request.db_request)
		return await performShow(self, show_request)

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performShow(db_instance, show_request):

	check_location = f"{db_instance.container_root}{show_request.path}"

	if not os.path.exists(check_location):
		res = dict(
			code=400,
			status="error",
			msg=f"no tree path found at '{check_location}'",
		)
		return db_instance.response(status=400, body=json.dumps(res))

	root = {'supercontainer': {},'container': []}
	tree = await getContainer(root, check_location, recursive=show_request.recursive)

	res = dict(
		code=200,
		status="showed",
		path=check_location,
		recursive=show_request.recursive,
		tree=tree
	)

	if db_instance.Server.action_logging:
		db_instance.Server.Logger.info(f"showed tree: path={check_location}, recursive={str(show_request.recursive)}")
	return db_instance.response(status=200, body=json.dumps(res))

async def getContainer(tree, folder_path, recursive=False):
	for file in os.listdir(folder_path):

		#is container
		if file.endswith('.phaazedb'):
			file = file.split('.phaazedb')[0]
			tree['container'].append(file)

		#is supercontainer
		else:
			if recursive:
				tree['supercontainer'][file] = await getContainer(dict(supercontainer={}, container=[]), f"{folder_path}/{file}", recursive=recursive)
			else:
				tree['supercontainer'][file] = {}

	return tree
