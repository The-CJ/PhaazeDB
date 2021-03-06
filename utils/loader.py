from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

from aiohttp.web import Request
from aiohttp.formdata import MultiDictProxy

class DBRequest(object):
	"""
		Main Object with all arguments and values for a WebRequest:Request
		contains the content based on a extraction method (JSON, POST, GET. etc...)
	"""
	def __init__(self, method:str):
		self.method = method
		self.success:bool = False
		self.error_msg:str = ""
		self.content:dict = dict()

	def setContent(self, content:dict) -> None:
		if type(content) not in [dict, MultiDictProxy]: raise AttributeError("need a dict type")
		self.content = content

	def get(self, *arg) -> Any:
		if len(arg) == 0:
			raise AttributeError("Missing key for get")
		else:
			if len(arg) > 1: return self.content.get(arg[0], arg[1])
			else: return self.content.get(arg[0])

async def jsonContent(cls:"PhaazeDatabase", WebRequest:Request) -> DBRequest:
	DBReq = DBRequest("JSON")

	try:
		DBReq.setContent(await WebRequest.json())
		DBReq.success = True
		return DBReq
	except Exception as e:
		DBReq.error_msg = str(e)
		return DBReq

async def postContent(cls:"PhaazeDatabase", WebRequest:Request) -> DBRequest:
	DBReq = DBRequest("POST")

	try:
		DBReq.setContent(await WebRequest.post())
		DBReq.success = True
		return DBReq
	except Exception as e:
		DBReq.error_msg = str(e)
		return DBReq
