from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import asyncio, json
from utils.errors import MissingOptionField, SysStoreError, SysLoadError, ContainerNotFound, InvalidValue
from utils.security import password
from aiohttp.web import Request, Response
from utils.loader import DBRequest
from utils.container import Container

class OptionRequest(object):
	""" Contains informations for a valid option request,
		does not mean the option actully exists or given parameter are possible"""
	def __init__(self, DBReq:DBRequest):
		self.option:str = None
		self.value:str = None

		self.getOption(DBReq)
		self.getValue(DBReq)

	def getOption(self, DBReq:DBRequest):
		self.option = DBReq.get("option", None)
		if type(self.option) is not str:
			self.option = None

		if not self.option: raise MissingOptionField()

	def getValue(self, DBReq:DBRequest):
		self.value = DBReq.get("value", None)
		if not self.value:
			self.value = None

async def option(cls:"PhaazeDatabase", WebRequest:Request, DBReq:DBRequest) -> Response:
	""" Used to change options on the fly """

	# prepare request for a valid option process
	try:
		DBOptionRequest:OptionRequest = OptionRequest(DBReq)
		return await performOption(cls, DBOptionRequest)

	except (MissingOptionField, SysStoreError, SysLoadError, ContainerNotFound, InvalidValue) as e:
		res = dict(
			code = e.code,
			status = e.status,
			msg = e.msg()
		)
		return cls.response(status=e.code, body=json.dumps(res))

	except Exception as ex:
		return await cls.criticalError(ex)

async def performOption(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:

	if DBOptionRequest.option == "log":
		return await performLogging(cls, DBOptionRequest)

	elif DBOptionRequest.option == "shutdown":
		return await performShutdown(cls, DBOptionRequest)

	elif DBOptionRequest.option == "store":
		return await performStore(cls, DBOptionRequest)

	elif DBOptionRequest.option == "password":
		return await performPassword(cls, DBOptionRequest)

	elif DBOptionRequest.option == "config":
		return await performConfig(cls, DBOptionRequest)

	elif DBOptionRequest.option in ["keep_alive", "save_interval", "allowed_ips"]:
		return await performSetConfig(cls, DBOptionRequest)

	else:
		raise MissingOptionField(True)

async def performLogging(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:

	# fix value from call
	if DBOptionRequest.value != None:
		cls.PhaazeDBS.action_logging = bool(DBOptionRequest.value)
	# toggle
	else:
		cls.PhaazeDBS.action_logging = False if cls.PhaazeDBS.action_logging else True

	vv:str = "active" if cls.PhaazeDBS.action_logging else "disabled"
	cls.PhaazeDBS.Logger.info(f"Action logging now: {vv}")

	res:dict = dict(
		code=200,
		status="success",
		msg=f"'action_logging' is now {vv}"
	)
	return cls.response(status=200, body=json.dumps(res))

async def performShutdown(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:

	asyncio.ensure_future(cls.PhaazeDBS.stop())

	res:dict = dict(
		code=200,
		status="success",
		msg="DB is sutting down"
	)
	return cls.response(status=200, body=json.dumps(res))

async def performStore(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:

	if DBOptionRequest.value:
		if type(DBOptionRequest.value) == str:
			DBOptionRequest.value = DBOptionRequest.value.strip("/")
		SelectedContainer:Container = await cls.load(DBOptionRequest.value)
		if SelectedContainer.status == "sys_error": raise SysLoadError(DBOptionRequest.value)
		elif SelectedContainer.status == "not_found": raise ContainerNotFound(DBOptionRequest.value)
	else:
		SelectedContainer = None

	# one
	if SelectedContainer:
		success:bool = await SelectedContainer.save()
		if success:
			res:dict = dict(
				code=200,
				status="success",
				msg=f"forced store of '{DBOptionRequest.value}' complete"
			)
			return cls.response(status=200, body=json.dumps(res))

		else:
			raise SysStoreError(DBOptionRequest.value)

	# all
	success:bool = await cls.storeAllContainer(remove_from_ram=False)
	if success:
		res:dict = dict(
			code=200,
			status="success",
			msg="forced store of all active container complete"
		)
		return cls.response(status=200, body=json.dumps(res))

	else:
		res = dict(
			code=500,
			status="critical_error",
			msg="forced store of all container failed at least once"
		)
		return cls.response(status=500, body=json.dumps(res))

async def performPassword(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:

	if not DBOptionRequest.value:
		raise InvalidValue()

	new_db_token:str = password(DBOptionRequest.value)

	# set to current
	cls.PhaazeDBS.token = new_db_token

	# overwrite password file
	FileWriter = open(f"{cls.container_root}DBTOKEN", "wb")
	FileWriter.write(bytes(new_db_token, "UTF-8"))
	FileWriter.close()

	res:dict = dict(
		code=200,
		status="success",
		msg="new password set"
	)
	return cls.response(status=200, body=json.dumps(res))

async def performConfig(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:
	config:dict = dict(
		address=cls.PhaazeDBS.address,
		port=cls.PhaazeDBS.port,
		root=cls.container_root,
		keep_alive=cls.keep_alive,
		save_interval=cls.save_interval,
		allowed_ips=cls.PhaazeDBS.allowed_ips
	)
	res:dict = dict(
		code=200,
		config=config,
		status="success",
		msg="returned current configs"
	)
	cls.PhaazeDBS.Logger.info(f"Returned settings")
	return cls.response(status=200, body=json.dumps(res))

async def performSetConfig(cls:"PhaazeDatabase", DBOptionRequest:OptionRequest) -> Response:
	new_value:Any = None

	if not DBOptionRequest.value:
		raise InvalidValue()

	if DBOptionRequest.option == "keep_alive":
		cls.keep_alive = new_value = int(DBOptionRequest.value)

	if DBOptionRequest.option == "save_interval":
		cls.save_interval = new_value = int(DBOptionRequest.value)

	if DBOptionRequest.option == "allowed_ips":
		if type(DBOptionRequest.value) == list:
			nl:list = DBOptionRequest.value
			new_value = nl
		elif type(DBOptionRequest.value) == str:
			nl:list = DBOptionRequest.value.split(",")
			new_value = nl
		else: raise InvalidValue()

		cls.PhaazeDBS.allowed_ips = nl

	res:dict = dict(
		code=200,
		changed=DBOptionRequest.option,
		new_value=new_value,
		status="success",
		msg="configuration updated"
	)
	cls.PhaazeDBS.Logger.info(f"Changed settings {DBOptionRequest.option} => {new_value}")

	try:
		raw_configs:bytes = open(cls.PhaazeDBS.config_path, "rb").read()
		configs:dict = json.loads(raw_configs.decode("UTF-8"))

		configs['address'] = str(cls.PhaazeDBS.address)
		configs['port'] = int(cls.PhaazeDBS.port)
		configs['root'] = str(cls.container_root)
		configs['keep_alive'] = int(cls.keep_alive)
		configs['save_interval'] = int(cls.save_interval)
		configs['allowed_ips'] = list(cls.PhaazeDBS.allowed_ips)

		json.dump( configs, open(cls.PhaazeDBS.config_path, "w"), indent=4, sort_keys=True)
		cls.PhaazeDBS.Logger.info(f"Successfull saved changed to config file")

	except Exception as e:
		res['error'] = str(e)
		res['msg'] += ", but error while saving to config file"
		cls.PhaazeDBS.Logger.critical(f"Error while trying to save configs: {str(e)}")

	finally:
		return cls.response(status=200, body=json.dumps(res))
