from nluas.core_solver import CoreProblemSolver
from nluas.core_specializer import *
import sys, traceback
from nluas.ntuple_transporter import NtupleTransporter
from nluas.analyzer_proxy import Analyzer
from nluas.spell_checker import SpellChecker

analyzer = Analyzer('http://localhost:8090')
specializer = CoreSpecializer()
transporter = NtupleTransporter()
solver = CoreProblemSolver()


#sentences = ["he moved the block into the room."]

sentences = ["he moved to the box.",
			 "is mud brown?",
			 "my sister is a doctor."
			 "he ran to a block.",
			 "he walked into the room.",
			 "he moved into the room.",
			 "move to the box!",
			 "the big box is near the blue block.",
			 "which box is red?",
			 "is the man big?",
			 "the woman ran into the box.",
			 "is he a man?",
			 "the woman ran behind the red block.",
			 "he moved the block into the room."]
		 

template = "\n--------------------------\n{}\n"


errors = 0
for sentence in sentences:
	try:
		print(template.format(sentence))
		#print("\n----------------------------")
		#print(sentence)
		#print("\n")
		semspecs = analyzer.parse(sentence)
		for fs in semspecs:
			try:
				ntuple = specializer.specialize(fs)

				js = transporter.convert_to_JSON(ntuple)
				solver.solve(js)
				break
			except Exception:
				pass
				#traceback.print_exc()
	except Exception:
		traceback.print_exc()
		errros += 1

print("\n\n{} errors.".format(errors))
