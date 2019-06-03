import json, traceback

async def criticalError(cls, Ex):
	content:dict = dict(code=500, status="critical_error", msg="unknown error")
	cls.PhaazeDBS.Logger.critical(f"Unknown error: {str(traceback.format_exc())}")
	return cls.response(status=500, body=json.dumps(content))

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

class MissingIntoField(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'into' field"

class MissingNameField(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'name' field"

class MissingOptionField(Exception):
	def __init__(self, *arg):
		self.unknown = True if arg else False
		self.code = 400
		self.status = "error"

	def msg(self, *arg):
		if self.unknown:
			return "invalid value in 'option' field"
		else:
			return "missing 'option' field"

class MissingStoreInJoin(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "missing 'store' in join"

class MissingUpdateContent(Exception):
	def __init__(self, *arg):
		self.empty_field = True if arg else False
		self.code = 400
		self.status = "error"

	def msg(self, *arg):
		if self.empty_field:
			return "unnamed or empty field in 'content' field"
		else:
			return "missing 'content' field as valid json-object or exec() string"

class MissingImportFile(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg):
		return "missing content file as key 'phzdb' in post"

class ContainerAlreadyExists(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return f"container '{self.container}' already exists"

class InvalidJoin(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "invalid or missing content in 'join' field"

class InvalidLimit(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "invalid value for 'limit', number must be > 0"

class InvalidValue(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return "invalid value for field 'value'"

class InvalidContent(Exception):
	def __init__(self, *arg):
		self.empty_field = True if arg else False
		self.code = 400
		self.status = "error"

	def msg(self, *arg):
		if self.empty_field:
			return "unnamed or empty field in 'content' field"
		else:
			return "invalid or missing 'content' as valid json-object"

class InvalidUpdateExec(Exception):
	def __init__(self, *arg):
		self.catch = arg[0] if arg else None
		self.code = 400
		self.status = "error"

	def msg(self, *arg):
		return f"exec() string for in 'content' field has throw a exception: {self.catch}"

class SysLoadError(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB could not load container file: '{self.container}'"

class SysStoreError(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB could not store data in container file: '{self.container}'"

class SysCreateError(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB could not create container file: '{self.container}'"

class ContainerNotFound(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 404
		self.status = "error"

	def msg(self, *arg): return f"container '{self.container}' not found"

class CantAccessContainer(PermissionError):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.type = arg[1] if len(arg) > 1 else "container"
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"system can't access {self.type}: '{self.container}'"

class ContainerBroken(Exception):
	def __init__(self, *arg):
		self.container = arg[0] if arg else None
		self.code = 500
		self.status = "critical_error"

	def msg(self, *arg): return f"DB container file: '{self.container}' seems broken"

class ImportNoActiveContainer(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return f"import cant continue, no active container set"

class ImportEntryExists(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return f"import cant continue, a entry already exists"

class InvalidImportEntry(Exception):
	def __init__(self, *arg):
		self.code = 400
		self.status = "error"

	def msg(self, *arg): return f"broken entry for import"
