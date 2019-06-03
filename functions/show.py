from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import json, os
from utils.errors import CantAccessContainer
from aiohttp.web import Request, Response
from utils.loader import DBRequest

class ShowRequest(object):
	"""
		Contains informations for a valid show request,
		does not mean if can be executed without errors
	"""
	def __init__(self, DBReq:DBRequest):
		self.recursive:bool = False
		self.path:str = None

		self.getRecursive(DBReq)
		self.getPath(DBReq)

	def getRecursive(self, DBReq:DBRequest) -> None:
		self.recursive = DBReq.get("recursive",None)
		if type(self.recursive) is not bool:
			self.recursive = bool(self.recursive)

	def getPath(self, DBReq:DBRequest) -> None:
		self.path = DBReq.get("path", "")
		if type(self.path) is not str:
			self.path = str(self.path)

		self.path = self.path.replace('..', '')
		self.path = self.path.strip('/')

		if not self.path: self.path = ""

async def show(cls:"PhaazeDatabase", WebRequest:Request) -> Response:
	"""
		Shows container hierarchy from 'name' or all if not defined
	"""
	try:
		DBShowRequest:Request = ShowRequest(WebRequest.DBReq)
		return await performShow(cls, DBShowRequest)

	except (CantAccessContainer) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performShow(cls:"PhaazeDatabase", DBShowRequest:ShowRequest) -> Response:

	check_location:str = f"{cls.container_root}{DBShowRequest.path}"

	if not os.path.exists(check_location):
		res = dict(
			code=400,
			status="error",
			msg=f"no tree path found at '{show_request.path}'",
		)
		return cls.response(status=400, body=json.dumps(res))

	root:dict = {'supercontainer': {},'container': [], 'unusable': []}
	tree:dict = await getContainer(root, check_location, recursive=show_request.recursive)

	res:dict = dict(
		code=200,
		status="showed",
		path=DBShowRequest.path,
		recursive=DBShowRequest.recursive,
		tree=tree
	)

	if cls.Server.action_logging:
		cls.Server.Logger.info(f"showed tree: path={show_request.path}, recursive={str(show_request.recursive)}")
	return cls.response(status=200, body=json.dumps(res))

async def getContainer(tree, folder_path, recursive=False):
	try:
		container_list = os.listdir(folder_path)
	except PermissionError:
		raise CantAccessContainer(folder_path,"supercontainer")

	for check_object in container_list:
		# is container
		if check_object.endswith('.phaazedb'):
			check_object = check_object.split('.phaazedb')[0]
			tree['container'].append(check_object)

		# is supercontainer and a folder
		elif os.path.isdir(f"{folder_path}/{check_object}"):
			if recursive:
				tree['supercontainer'][check_object] = await getContainer(dict(supercontainer={}, container=[], unusable=[]), f"{folder_path}/{check_object}", recursive=recursive)
			else:
				tree['supercontainer'][check_object] = {}

		# it's nothing phaazeDB should handle
		else:
			tree['unusable'].append(check_object)

	return tree
