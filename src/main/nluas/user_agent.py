from nluas.core_specializer import *
from nluas.core_agent import *
from nluas.analyzer_proxy import *
from nluas.core_specializer import *
from nluas.ntuple_decoder import NtupleDecoder
import sys

class UserAgent(CoreAgent):
	def __init__(self, args):
		CoreAgent.__init__(self, args)
		self.initialize_UI()
		self.solve_destination = "{}_{}".format(self.federation, "ProblemSolver")

	def initialize_UI(self):
		self.analyzer = analyzer=Analyzer('http://localhost:8090')
		self.specializer=CoreSpecializer()
		self.decoder = NtupleDecoder()

	def process_input(self, msg):
		try:
			semspecs = self.analyzer.parse(msg)
			for fs in semspecs:
				try:
					ntuple = self.specializer.specialize(fs)
					json_ntuple = self.decoder.convert_to_JSON(ntuple)
					self.transport.send(self.solve_destination, json_ntuple)
					break
				except Exception as e:
					print(e)
		except Exception as e:
			print(e)

	def callback(self, ntuple):
		print("Clarification requested.")
		#print(ntuple)
		decoded = self.decoder.convert_JSON_to_ntuple(ntuple)
		#print(decoded)

	def prompt(self):
		while True:
			msg = input("> ")
			if msg == "q":
				quit()
			self.process_input(msg)





