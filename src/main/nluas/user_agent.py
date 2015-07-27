from nluas.core_specializer import *
from nluas.core_agent import *
from nluas.analyzer_proxy import *

class UserAgent(CoreAgent):
	def __init__(self, name, analyzer, specializer, decoder):
		CoreAgent.__init__(self, name=name)
		self.analyzer = analyzer
		self.specializer = specializer
		self.decoder = decoder

	def process_input(self, msg):
		try:
			semspecs = self.analyzer.parse(msg)
			for fs in semspecs:
				try:
					ntuple = self.specializer.specialize(fs)
					json_ntuple = self.decoder.convert_to_JSON(ntuple)
					self.transport.send("ProblemSolver", json_ntuple)
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





