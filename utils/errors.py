import asyncio, json

async def unauthorised(self):
	content = dict(code=401, status="error", msg="unauthorised")
	return self.response(body=json.dumps(content))

