import asyncio, json

async def unauthorised(self):
	content = dict(code=401, status="error", msg="unauthorised")
	return self.response(status=401, body=json.dumps(content))

async def missingFunction(self):
	content = dict(code=400, status="error", msg="missing 'action' field")
	return self.response(status=400, body=json.dumps(content))

async def unknownFunction(self):
	content = dict(code=400, status="error", msg="unknown value for 'action'")
	return self.response(status=400, body=json.dumps(content))

class MissingOfField(Exception):
	code = 400
	status = "error"
	def msg(*arg): return "missing 'of' field"

class MissingStoreInJoin(Exception):
	status = 400

class InvalidJoin(Exception):
	status = 400

class SysLoadError(Exception):
	code = 500
	status = "critical_error"
	def msg(*arg): return "DB could not load container file"

class ContainerNotFound(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 404
		self.status = "error"

	def msg(self, *arg): return f"container '{self.container}' not found"
