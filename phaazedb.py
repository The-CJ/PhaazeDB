__version__ = "2.0.1"

import json, sys, logging

from utils.cli import CliArgs
from utils.database import Database
from aiohttp import web

try: from systemd.journal import JournalHandler
except ImportError:	pass

class PhaazeDBServer(object):
	"""Contains all main parts: DB, main service and web interface"""
	def __init__(self):
		self.version = __version__

		self.Server = None
		self.Database = None
		self.Logger = None
		self.config = None

		self.adress = "0.0.0.0"
		self.port = 2000
		self.action_logging = False
		self.allowed_ips = []

		self.loadConfig()
		self.loadLogging()
		self.loadDatabase()
		self.loadServer()

	def loadConfig(self):
		config_file = CliArgs.get("config", "config.json")
		try:
			configs = open(config_file, "rb").read()
			c = json.loads(configs.decode("UTF-8"))
		except FileNotFoundError:
			print(f"file '{config_file}' could not be found")
			c = dict()
		except json.decoder.JSONDecodeError:
			print(f"file '{config_file}' could not be loaded as a config file")
			c = dict()
		finally:
			self.config = c

			self.adress = c.get("adress", "0.0.0.0")
			self.port = c.get("port", 2000)
			self.action_logging = c.get("logging", False)
			self.allowed_ips = c.get("allowed_ips", [])

	def loadLogging(self):
		self.Logger = logging.getLogger('PhaazeDB')
		self.Logger.setLevel(logging.DEBUG)
		SHF = logging.Formatter("[%(levelname)s]: %(message)s")
		if CliArgs.get('logging', 'console') == "systemd" and 'systemd' in sys.modules:
			JH = JournalHandler()
			JH.setFormatter(SHF)
			self.Logger.addHandler(JH)
		else:
			SH = logging.StreamHandler()
			SH.setFormatter(SHF)
			self.Logger.addHandler(SH)

	def loadDatabase(self):
		self.Database = Database(self)

	def loadServer(self):
		self.Server = web.Application()

		self.Server.router.add_route('GET', '/admin{x:.*}', self.Database.interface)
		self.Server.router.add_route('GET', '/favicon.ico', self.Database.interface)
		self.Server.router.add_route('*', '/{x:.*}', self.Database.process)

	def start(self):
		self.Logger.info(f"Starting PhaazeDB v{self.version}")
		self.Logger.info(f"Running on port: {self.port}")
		if self.allowed_ips: self.Logger.info(f"Allowed IP's: {self.allowed_ips}")
		self.Logger.info(f"Action Logging: {self.action_logging}")

		web.run_app(self.Server, port=self.port, print=False)

	async def stop(self):
		self.Logger.info(f"Shutdown started...")
		await self.Server.shutdown()
		await self.Database.stop()
		self.Logger.info(f"Shutdown finished")
		exit(1)

if __name__ == '__main__':
	PhaazeDB = PhaazeDBServer()
	PhaazeDB.start()
