import asyncio, json, traceback

async def criticalError(self, Ex):
	content = dict(code=500, status="critical_error", msg="unknown error")
	exception = traceback.format_exc()
	self.Server.Logger.critical(f"Unknown error: {str(exception)}")
	return self.response(status=500, body=json.dumps(content))

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
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'of' field"

class MissingNameField(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'name' field"

class MissingStoreInJoin(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'store' in join"

class ContainerAlreadyExists(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 404
		self.status = "error"

	def msg(self, *arg): return f"container '{self.container}' already exists"

class InvalidJoin(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "invalid or missing content in 'join' field"

class SysLoadError(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB could not load container file: {self.container}"

class SysCreateError(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB could not create container file: {self.container}"

class ContainerNotFound(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 404
		self.status = "error"

	def msg(self, *arg): return f"container '{self.container}' not found"
