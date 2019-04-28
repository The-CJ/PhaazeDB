import asyncio, json, os
from utils.errors import MissingPathField

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
		self.path = self.path.replace('..', '')
		self.path = self.path.strip('/')

		if not self.path: raise MissingPathField()

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
		self.logger.info(f"showed tree: path={path}, recursive={str(recursive)}")
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
