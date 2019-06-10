__version__ = "2.0.1"

import json, sys, logging

from utils.cli import CliArgs
from utils.database import Database as PhaazeDatabase
from aiohttp.web import Application, run_app

try: from systemd.journal import JournalHandler
except ImportError:	pass

class PhaazeDBServer(object):
	"""Contains all main parts: DB main service and web interface"""
	def __init__(self):
		self.version:str = __version__

		self.Server:Application = None
		self.Database:PhaazeDatabase = None
		self.Logger:logging.Logger = None
		self.config:dict = None
		self.config_path:str = None

		self.token:str = None

		self.address:str = "0.0.0.0"
		self.port:int = 2000
		self.action_logging:bool = False
		self.allowed_ips:list = []

		self.loadLogging()
		self.loadConfig()
		self.loadDatabase()
		self.loadServer()

	def loadLogging(self) -> None:
		self.Logger = logging.getLogger('PhaazeDB')
		self.Logger.setLevel(logging.DEBUG)
		SHF:logging.Logger = logging.Formatter("[%(levelname)s]: %(message)s")
		if CliArgs.get('logging', 'console') == "systemd" and 'systemd' in sys.modules:
			JH:JournalHandler = JournalHandler()
			JH.setFormatter(SHF)
			self.Logger.addHandler(JH)
		else:
			SH:logging.StreamHandler = logging.StreamHandler()
			SH.setFormatter(SHF)
			self.Logger.addHandler(SH)

	def loadConfig(self) -> None:
		self.config_path = CliArgs.get("config", "config.json")
		try:
			configs:str = open(self.config_path, "rb").read()
			c:dict = json.loads(configs.decode("UTF-8"))
		except FileNotFoundError:
			self.Logger.critical(f"file '{self.config_path}' could not be found")
			c:dict = dict()
		except json.decoder.JSONDecodeError:
			self.Logger.critical(f"file '{self.config_path}' could not be loaded as a config file")
			c:dict = dict()
		except:
			self.Logger.critical(f"unexpected error while loading '{self.config_path}' as config file")
			c:dict = dict()
		finally:
			self.config = c

			self.address = c.get("address", "0.0.0.0")
			self.port = c.get("port", 2000)
			self.action_logging = c.get("logging", False)
			self.allowed_ips = c.get("allowed_ips", [])

	def loadToken(self) -> None:
		# token is saved in database root
		try:
			token_file_path = f"{self.Database.container_root}DBTOKEN"
			self.token = open(token_file_path, "r").read()
			self.Logger.info("Loaded db token")

		except Exception as e:
			self.Logger.critical(f"critical error while loading database token: {str(e)}")
			self.Logger.critical(f"running without token, set on as soon as possible")
			self.Logger.critical("make DB call: {action:'option', option:'password', value:'[your_new_password]'}")
			self.token = None

	def loadDatabase(self) -> None:
		self.Database = PhaazeDatabase(self)
		self.Database.setRoot(self.config.get("root", None))
		self.Database.setAliveTime(self.config.get("keep_alive", None))
		self.Database.setSaveInterval(self.config.get("save_interval", None))
		self.loadToken()

	def loadServer(self) -> None:
		self.Server = Application()

		self.Server.router.add_route('GET', '/admin{x:.*}', self.Database.interface)
		self.Server.router.add_route('GET', '/favicon.ico', self.Database.interface)
		self.Server.router.add_route('*', '/{x:.*}', self.Database.process)

		self.Server.middlewares.append( self.Database.mainHandler )

	def start(self) -> None:
		self.Logger.info(f"Starting PhaazeDB v{self.version}")
		self.Logger.info(f"Running on port: {self.port}")
		if self.allowed_ips: self.Logger.info(f"Allowed IP's: {self.allowed_ips}")
		self.Logger.info(f"Action Logging: {self.action_logging}")

		run_app(self.Server, host=self.address, port=self.port, print=False)

	async def stop(self) -> None:
		self.Logger.info(f"Shutdown started...")

		# close db and save all changes
		await self.Database.stop()

		await self.Server.shutdown()
		await self.Server.cleanup()

		self.Logger.info(f"Shutdown finished")
		sys.exit()

if __name__ == '__main__':
	PhaazeDB = PhaazeDBServer()
	PhaazeDB.start()
