import json, sys, os, logging

from utils.cli import CliArgs
from utils.database import Database
from aiohttp import web

try: from systemd.journal import JournalHandler
except ImportError:	pass

class PhaazeDBServer(object):
	"""Contains all main parts: DB, main service and web interface"""
	def __init__(self):
		self.Server = None
		self.Database = None
		self.Logger = None
		self.config = None

		self.loadConfig()
		self.loadLogging()

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

	def start(self):
		pass

	def stop(self):
		pass

def startServer():
	#check for DATABASE folder
	try:
		f = os.listdir('DATABASE/')
	except:
		os.mkdir('DATABASE')

	#make app
	DB = Database(config=configs)
	SERVER = web.Application()

	#web interface route
	SERVER.router.add_route('GET', '/admin{useless:.*}', DB.interface)
	SERVER.router.add_route("GET", "/favicon.ico", DB.interface)
	#main route
	SERVER.router.add_route('*', '/{useless:.*}', DB.process)

	#start
	DB.logger.info(f"Starting PhaazeDB v{DB.version}")
	DB.logger.info(f"Running on port: {configs.get('port', 3000)}")
	if configs.get("allowed_ips", []) != []:
		ips = configs.get("allowed_ips", [])
		ips_str = ", ".join("["+ip+"]" for ip in ips)
	else:
		ips_str = "--ALL--"
	DB.logger.info(f"Allowed IP's: {ips_str}")
	DB.logger.info(f"Action Logging: {DB.log}")

	web.run_app(SERVER, port=configs.get('port', 3000), print=False)

if __name__ == '__main__':
	PhaazeDB = PhaazeDBServer()
	PhaazeDB.start()
	input("e")
