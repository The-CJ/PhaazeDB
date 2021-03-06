import sys, re

class CliArguments(object):
	"""
		Contains arguments added by programm start
	"""
	def __init__(self):
		self.args:dict = dict()

		option_re = re.compile(r'^--(.+?)=(.*)$')
		for arg in sys.argv[1:]:
			d = option_re.match(arg)
			if d != None: self.args[d.group(1)] = d.group(2)

	def get(self, *arg) -> str:
		if len(arg) == 0:
			return self.args
		else:
			if len(arg) > 1: return self.args.get(arg[0], arg[1])
			else: return self.args.get(arg[0])

CliArgs:CliArguments = CliArguments()
