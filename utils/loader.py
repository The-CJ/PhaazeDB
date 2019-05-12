class DBContent(object):
	"""Main Object with all arguments and values for one request """
	def __init__(self):
		self.success = False
		self.error_msg = ""
		self.content = dict()

	def setContent(self, content):
		self.content = content

	def get(self, *arg):
		if len(arg) == 0:
			raise AttributeError("Missing key for get")
		else:
			if len(arg) > 1: return self.content.get(arg[0], arg[1])
			else: return self.content.get(arg[0])

async def jsonContent(self, request):
	db_content = DBContent()

	try:
		db_content.setContent(await request.json())
		db_content.success = True
		return db_content
	except Exception as e:
		db_content.error_msg = str(e)
		return db_content
