import json

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

	except () as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performStoreExport(self, store_export_request):
	pass
