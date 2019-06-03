from typing import Any

class DBRequest(object):
	"""
		Main Object with all arguments and values for a request
		contains the content based on a extraction method (JSON, POST, GET. etc...)
	"""
	def __init__(self):
		self.success:bool = False
		self.error_msg:str = ""
		self.content:dict = dict()

	def setContent(self, content) -> None:
		self.content = content

	def get(self, *arg) -> Any:
		if len(arg) == 0:
			raise AttributeError("Missing key for get")
		else:
			if len(arg) > 1: return self.content.get(arg[0], arg[1])
			else: return self.content.get(arg[0])

async def jsonContent(self, request):
	db_content = DBRequest()

	try:
		db_content.setContent(await request.json())
		db_content.success = True
		return db_content
	except Exception as e:
		db_content.error_msg = str(e)
		return db_content

async def postContent(self, request):
	db_content = DBRequest()

	try:
		db_content.setContent(await request.post())
		db_content.success = True
		return db_content
	except Exception as e:
		db_content.error_msg = str(e)
		return db_content
