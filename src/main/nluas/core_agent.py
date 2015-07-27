from nluas.Transport import *
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="assign a name to this agent")
parser.add_argument("logfile", type=str, help="indicate logfile path for logging output")
parser.add_argument("loglevel", type=str, help="indicate loglevel for logging output: warn, debug, error")
parser.add_argument("logagent", type=str, help="indicate agent responsible for logging output")
args = parser.parse_args()


class CoreAgent(object):

	def __init__(self, name, federation, logfile, loglevel, logagent):
		self.name = name
		self.federation = federation
		self.address = "{}_{}".format(self.federation, self.name)
		self.transport = Transport(self.address)
		self.logfile = logfile
		self.loglevel = loglevel
		self.logagent = logagent

	#def setup_parser(self):


	def callback(self, ntuple):
		print("{} received {}.".format(self.name, ntuple))

	def subscribe_mass(self, ports):
		for port in ports:
			self.transport.subscribe(port, self.callback)


