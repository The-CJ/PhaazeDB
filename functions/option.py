import asyncio, json, math
from utils.errors import MissingOptionField, SysStoreError, SysLoadError, ContainerNotFound, InvalidValue
from utils.security import password
from utils.cli import CliArgs

class OptionRequest(object):
	""" Contains informations for a valid option request,
		does not mean the option actully exists or given parameter are possible"""
	def __init__(self, db_req):
		self.option:str = None
		self.value:str = None

		self.getOption(db_req)
		self.getValue(db_req)

	def getOption(self, db_req):
		self.option = db_req.get("option", None)
		if type(self.option) is not str:
			self.option = None

		if not self.option: raise MissingOptionField()

	def getValue(self, db_req):
		self.value = db_req.get("value", None)
		if not self.value:
			self.value = None

async def option(self, request):
	""" Used to change options on the fly """

	# prepare request for a valid insert
	try:
		option_request = OptionRequest(request.db_request)
		return await performOption(self, option_request)

	except (MissingOptionField, SysStoreError, SysLoadError, ContainerNotFound, InvalidValue) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return self.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await self.criticalError(ex)

async def performOption(db_instance, option_request):

	if option_request.option == "log":
		return await performLogging(db_instance, option_request)

	elif option_request.option == "shutdown":
		return await performShutdown(db_instance, option_request)

	elif option_request.option == "store":
		return await performStore(db_instance, option_request)

	elif option_request.option == "password":
		return await performPassword(db_instance, option_request)

	elif option_request.option == "config":
		return await performConfig(db_instance, option_request)

	elif option_request.option in ["keep_alive", "save_interval", "allowed_ips"]:
		return await performSetConfig(db_instance, option_request)

	else:
		raise MissingOptionField(True)

async def performLogging(db_instance, option_request):

	# fix value from call
	if option_request.value != None:
		db_instance.Server.action_logging = bool(option_request.value)
	# toggle
	else:
		db_instance.Server.action_logging = False if db_instance.Server.action_logging else True

	vv = "active" if db_instance.Server.action_logging else "disabled"
	db_instance.Server.Logger.info(f"Action logging now: {vv}")

	res = dict(
		code=200,
		status="success",
		msg=f"'action_logging' is now {vv}"
	)
	return db_instance.response(status=200, body=json.dumps(res))

async def performShutdown(db_instance, option_request):

	asyncio.ensure_future(db_instance.Server.stop())

	res = dict(
		code=200,
		status="success",
		msg="DB is sutting down"
	)
	return db_instance.response(status=200, body=json.dumps(res))

async def performStore(db_instance, option_request):

	if option_request.value:
		if type(option_request.value) == str:
			option_request.value = option_request.value.strip("/")
		selected_container = await db_instance.load(option_request.value)
		if selected_container.status == "sys_error": raise SysLoadError(option_request.value)
		elif selected_container.status == "not_found": raise ContainerNotFound(option_request.value)
	else:
		selected_container = None

	# one
	if selected_container:
		success = await selected_container.save()
		if success:
			res = dict(
				code=200,
				status="success",
				msg=f"forced store of '{option_request.value}' complete"
			)
			return db_instance.response(status=200, body=json.dumps(res))

		else:
			raise SysStoreError(option_request.value)

	# all
	success = await db_instance.storeAllContainer(remove_from_ram=False)
	if success:
		res = dict(
			code=200,
			status="success",
			msg="forced store of all active container complete"
		)
		return db_instance.response(status=200, body=json.dumps(res))

	else:
		res = dict(
			code=500,
			status="critical_error",
			msg="forced store of all container failed at least once"
		)
		return db_instance.response(status=500, body=json.dumps(res))

async def performPassword(db_instance, option_request):

	if not option_request.value:
		raise InvalidValue()

	new_db_token = password(option_request.value)

	# set to current
	db_instance.Server.token = new_db_token

	# overwrite password file
	passwd_file = f"{db_instance.container_root}DBTOKEN"
	file_writer = open(passwd_file, "w")
	file_writer.write(new_db_token)
	file_writer.close()

	res = dict(
		code=200,
		status="success",
		msg="new password set"
	)
	return db_instance.response(status=200, body=json.dumps(res))

async def performConfig(db_instance, option_request):
	config = dict(
		address=db_instance.Server.address,
		port=db_instance.Server.port,
		root=db_instance.container_root,
		keep_alive=db_instance.keep_alive,
		save_interval=db_instance.save_interval,
		allowed_ips=db_instance.Server.allowed_ips
	)
	res = dict(
		code=200,
		config=config,
		status="success",
		msg="returned current configs"
	)
	db_instance.Server.Logger.info(f"Returned settings")
	return db_instance.response(status=200, body=json.dumps(res))

async def performSetConfig(db_instance, option_request):
	new_value = None
	if not option_request.value:
		raise InvalidValue()

	if option_request.option == "keep_alive":
		db_instance.keep_alive = new_value = int(option_request.value)

	if option_request.option == "save_interval":
		db_instance.save_interval = new_value = int(option_request.value)

	if option_request.option == "allowed_ips":
		if type(option_request.value) == list: nl = new_value = option_request.value
		elif type(option_request.value) == str: nl = new_value = option_request.value.split(",")
		else: raise InvalidValue()

		db_instance.Server.allowed_ips = nl

	res = dict(
		code=200,
		changed=option_request.option,
		new_value=new_value,
		status="success",
		msg="configuration updated"
	)
	db_instance.Server.Logger.info(f"Changed settings {option_request.option} => {new_value}")

	try:
		configs = open(db_instance.Server.config_path, "rb").read()
		c = json.loads(configs.decode("UTF-8"))

		c['address'] = str(db_instance.Server.address)
		c['port'] = int(db_instance.Server.port)
		c['root'] = str(db_instance.container_root)
		c['keep_alive'] = int(db_instance.keep_alive)
		c['save_interval'] = int(db_instance.save_interval)
		c['allowed_ips'] = list(db_instance.Server.allowed_ips)

		json.dump( c, open(db_instance.Server.config_path, "w"), indent=4, sort_keys=True)
		db_instance.Server.Logger.info(f"Successfull saved changed to config.file	")

	except Exception as e:
		res['error'] = str(e)
		res['msg'] += ", but error while saving"
		db_instance.Server.Logger.critical(f"Error while trying to save configs: {str(e)}")

	return db_instance.response(status=200, body=json.dumps(res))
