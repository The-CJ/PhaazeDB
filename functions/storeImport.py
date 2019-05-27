import json

async def storeImport(self, request):
	""" Used to update entry fields in a existing container """

	# prepare request for a valid search
	try:
		update_request = UpdateRequest(request.db_request)
		return await performUpdate(self, update_request)

	except (MissingOfField, InvalidLimit, MissingUpdateContent, SysLoadError, SysStoreError, ContainerNotFound, InvalidUpdateExec) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)
