import json, asyncio
from utils.errors import MissingImportFile

class ImportRequest(object):
	"""
		Contains informations for a valid import request
		does not mean other errors are impossible,
		also it's a bridge class for all incomming data object,
		to be proccessed and inserted into the right db
	"""
	def __init__(self, db_req):
		self.fileObject:None = None

		self.overwrite_container = False
		self.overwrite_entrys = False
		self.ignore_errors = False

		# for processing
		self.return_code = 102
		self.current_container = None
		self.errors = []

		self.getFile(db_req)
		self.getOverrides(db_req)
		self.getIgnore(db_req)

	def getFile(self, db_req):
		self.fileObject = db_req.get("phzdb", None)
		if not self.fileObject: raise MissingImportFile()

	def getOverrides(self, db_req):
		self.overwrite_container = db_req.get("overwrite_container", None)
		if type(self.overwrite_container) is not bool:
			self.overwrite_container = bool(self.overwrite_container)

		self.overwrite_entrys = db_req.get("overwrite_entrys", None)
		if type(self.overwrite_entrys) is not bool:
			self.overwrite_entrys = bool(self.overwrite_entrys)

	def getIgnore(self, db_req):
		self.ignore_errors = db_req.get("ignore_errors", None)
		if type(self.ignore_errors) is not bool:
			self.ignore_errors = bool(self.ignore_errors)

	# following are "bride" functions
	async def processLine(self, line):
		if line.startswith(b"ENTRY"): await self.proccessEntry(line)
		elif line.startswith(b"DEFAULT"): await self.proccessDefault(line)
		elif line.startswith(b"CONTAINER"): await self.proccessContainer(line)
		else:
			pass

	async def proccessEntry(self, line):
		print(line)

	async def proccessDefault(self, line):
		print(line)

	async def proccessContainer(self, line):
		print(line)

async def storeImport(self, request):
	"""
		Used to import data from file. file extention should be .phzdb
		but can be every type in therory
	"""
	# prepare request for a valid search
	try:
		store_import_request = ImportRequest(request.db_request)
		return await performImport(self, store_import_request)

	except (MissingImportFile) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performImport(db_instance, store_import_request):
	for line in store_import_request.fileObject.file:
		await store_import_request.processLine(line)

	res = dict(
		code=store_import_request.return_code,
		status="imported",
		errors=store_import_request.errors,
		overwrite_container=store_import_request.overwrite_container,
		overwrite_entrys=store_import_request.overwrite_entrys
	)

	db_instance.Server.Logger.info(f"todo")
	return db_instance.response(status=store_import_request.return_code, body=json.dumps(res))
