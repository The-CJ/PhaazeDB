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
	status = 400

class MissingStoreInJoin(Exception):
	status = 400

class InvalidJoin(Exception):
	status = 400

class SysLoadError(Exception):
	status = 500

class ContainerNotFound(Exception):
	status = 404
