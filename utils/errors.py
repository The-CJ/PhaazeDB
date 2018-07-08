import asyncio, json

async def unauthorised(self):
	content = dict(code=401, status="error", msg="unauthorised")
	return self.response(body=json.dumps(content))

async def missing_function(self):
	content = dict(code=400, status="error", msg="missing 'action' field")
	return self.response(body=json.dumps(content))

async def unknown_function(self):
	content = dict(code=400, status="error", msg="unknown value for 'action'")
	return self.response(body=json.dumps(content))
