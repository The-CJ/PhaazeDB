import json

async def default(self, request, _INFO):
	"""
		Used to set a new object as default for a container,
		values in default always get added to a select request,
		so values will always be there
	"""

	#get required vars (JSON -> POST based)

	#get container
	container_name = _INFO.get('_JSON', {}).get('container', None)
	if container_name == None:
		container_name = _INFO.get('_POST', {}).get('container', None)

	if container_name == None:
		container_name = ""
	else:
		container_name = str(container_name)

	container_name = container_name.replace('..', '')
	container_name = container_name.strip('/')

	#no container
	if container_name == "":
		res = dict(
			code=400,
			status="error",
			msg="missing 'container' field"
		)
		return self.response(status=400, body=json.dumps(res))

	new_default = _INFO.get('_JSON', {}).get('default', None)
	if new_default == None:
		new_default = _INFO.get('_POST', {}).get('default', None)

	if type(new_default) != dict:
		res = dict(
			code=400,
			status="error",
			msg="value 'default' must be a valid json object"
		)
		return self.response(status=400, body=json.dumps(res))

	try:
		#get container
		container = await self.load(container_name)

		#error handling
		if container.status == "sys_error":
			# this SHOULD never happen, but hey... just in case
			res = dict(
				code=500,
				status="error",
				msg="DB could not load container file."
			)
			return self.response(status=500, body=json.dumps(res))

		elif container.status == "not_found":
			res = dict(
				code=404,
				status="error",
				msg=f"container '{table_name}' not found"
			)
			return self.response(status=404, body=json.dumps(res))

		elif container.status == "success":

			container = container.content

		container["default"] = new_default

		#save everything
		finished = await self.store(container_name, container)

		if finished:
			res = dict(
				code=200,
				status="default set",
				container=container_name,
				default=new_default,
				msg=f"default set for container '{container_name}'"
			)
			if self.log != False:
				self.logger.info(f"default set for container '{container_name}'")
			return self.response(status=200, body=json.dumps(res))

		else:
			# this SHOULD never happen, but hey... just in case
			res = dict(
				code=500,
				status="error",
				msg="DB could not save your data."
			)
			if self.log != False:
				self.logger.critical(f"update entry(s) from '{table_name}' failed")
			return self.response(status=500, body=json.dumps(res))

	except:
		res = dict(
			code=500,
			status="error",
			msg="unknown server error"
		)
		if self.log != False:
			self.logger.critical(f"default set for container '{container_name}' failed")
		return self.response(status=500, body=json.dumps(res))
