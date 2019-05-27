import json, os
from utils.errors import CantAccessContainer
from functions.show import getContainer

from aiohttp.web import StreamResponse

class ExportRequest(object):
	""" Contains informations for a valid export request,
		does not mean the container exists """
	def __init__(self, db_req):
		self.container:str = None
		self.recursive:bool = False

		self.getRecursive(db_req)
		self.getContainter(db_req)

	def getRecursive(self, db_req):
		self.recursive = db_req.get("recursive",None)
		if type(self.recursive) is not bool:
			self.recursive = bool(self.recursive)

	def getContainter(self, db_req):
		self.container = db_req.get("container", "")
		if type(self.container) is not str:
			self.container = str(self.container)

		self.container = self.container.replace('..', '')
		self.container = self.container.strip('/')

		if not self.container: self.container = ""

async def storeExport(self, request):
	""" Used to export (super)container into a .pdb file and import it later again """

	# prepare request for a valid search
	try:
		store_export_request = ExportRequest(request.db_request)
		return await performStoreExport(self, store_export_request)

	except (CantAccessContainer) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performStoreExport(db_instance, store_export_request):
	check_location = f"{db_instance.container_root}{store_export_request.container}"

	if os.path.exists(f"{check_location}.phaazedb"):
		return await performExportDataGather(db_instance, store_export_request, [store_export_request.container])

	if not os.path.exists(check_location):
		res = dict(
			code=400,
			status="error",
			msg=f"no (super)container found: '{store_export_request.container}'",
		)
		return db_instance.response(status=400, body=json.dumps(res))

	root = {'supercontainer': {},'container': [], 'unusable': []}
	tree = await getContainer(root, check_location, recursive=store_export_request.recursive)

	container_list = splitTree(tree)

	return await performExportDataGather(db_instance, store_export_request, container_list)

def splitTree(root, before=""):
	container = [f"{before}{con}" for con in root['container']]
	for log in root["supercontainer"]:
		supercontainer = splitTree(root["supercontainer"][log], before=before+log+"/")
		for s in supercontainer: container.append(s)

	return container

async def performExportDataGather(db_instance, store_export_request, export_list):
	return_file = StreamResponse()
	return_file.content_type = "application/octet-stream"
	return_file.headers["CONTENT-DISPOSITION"] = f"attachment; filename={store_export_request.container}.pdb"

	for container in export_list:
		container = await db_instance.load(container)



		print(container.content)




















#
