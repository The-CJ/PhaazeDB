import json, asyncio
from utils.errors import MissingImportFile, ContainerAlreadyExists, SysCreateError, SysLoadError, ContainerNotFound, ImportNoActiveContainer
from functions.create import makeNewContainer

class ImportRequest(object):
	"""
		Contains informations for a valid import request
		does not mean other errors are impossible,
		also it's a bridge class for all incomming data object,
		to be proccessed and inserted into the right db
	"""
	def __init__(self, db_req, db_instance):
		self.fileObject:None = None
		self.db_link:db_instance = db_instance

		self.overwrite_container = False
		self.overwrite_entrys = False
		self.ignore_errors = False

		# for processing
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
		try:
			if line.startswith(b"ENTRY:"): await self.proccessEntry(line)
			elif line.startswith(b"DEFAULT:"): await self.proccessDefault(line)
			elif line.startswith(b"CONTAINER:"): await self.proccessContainer(line)
			else: pass
		except json.decoder.JSONDecodeError as e:
			print(e)

	async def proccessEntry(self, line):
		return
		print(line)

	async def proccessDefault(self, line):
		if not self.current_container:
			if self.ignore_errors:
				self.errors.append(f"can't set default, not active container -> skipping")
				return False
			else:
				raise ImportNoActiveContainer()

		default = json.loads(line[8:][:-2])
		container = await self.db_link.load(self.current_container)

		if container.status == "sys_error": raise SysLoadError(self.current_container)
		elif container.status == "not_found": raise ContainerNotFound(self.current_container)
		elif container.status == "success":	container = container.content

		container['default'] = default

		return True

	async def proccessContainer(self, line):
		container = await self.db_link.load(json.loads(line[10:][:-2]))
		if container.status != "not_found" and not self.overwrite_container:
			if self.ignore_errors:
				self.errors.append(f"container already exists: '{container.name}' -> set active anyway")
				self.current_container = container.name
				return False
			else:
				raise ContainerAlreadyExists(container.name)

		created = await makeNewContainer(self.db_link, container.name)
		if not created:
			self.db_link.Server.Logger.critical(f"create container '{container.name}' failed")
			raise SysCreateError(container.name)

		self.current_container = container.name
		return True

async def storeImport(self, request):
	"""
		Used to import data from file. file extention should be .phzdb
		but can be every type in therory
	"""
	# prepare request for a valid import
	try:
		store_import_request = ImportRequest(request.db_request, self)
		return await performImport(self, store_import_request)

	except (MissingImportFile, ContainerAlreadyExists, SysCreateError, SysLoadError, ContainerNotFound, ImportNoActiveContainer) as e:
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

	await db_instance.storeAllContainer()

	res = dict(
		code=200,
		status="imported",
		errors=store_import_request.errors,
		ignore_errors=store_import_request.ignore_errors,
		overwrite_container=store_import_request.overwrite_container,
		overwrite_entrys=store_import_request.overwrite_entrys
	)

	db_instance.Server.Logger.info(f"todo")
	return db_instance.response(status=200, body=json.dumps(res))
