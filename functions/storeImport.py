import json, asyncio
from utils.errors import MissingImportFile



async def storeImport(self, request):
	"""
		Used to import data from file. file extention should be .phzdb
		but can be every type in therory
	"""
	# prepare request for a valid search
	try:

		return await performImport(self, request)

	except (MissingImportFile) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

class ImportManager(object):
	""" lets call this a bridge class for all incomming data object to be proccessed and inserted into the right db """
	def __init__(self, db):
		self.db = db
		self.current_db = None

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

async def performImport(db_instance, request):
	content = await request.post()
	phzdb = content.get("phzdb", None)
	if not phzdb:
		raise MissingImportFile()

	IM = ImportManager(db_instance)

	for line in phzdb.file:
		await IM.processLine(line)
