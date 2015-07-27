from nluas.core_specializer import *
from nluas.core_agent import *
from nluas.analyzer_proxy import *
from nluas.core_solver import CoreProblemSolver
from nluas.ntuple_decoder import NtupleDecoder
from nluas.user_agent import UserAgent
import sys

"""
user_agent = UserAgent("AgentUI", analyzer=Analyzer('http://localhost:8090'), 
						specializer=CoreSpecializer(), decoder=NtupleDecoder())

solver = CoreProblemSolver(name="ProblemSolver")

user_agent.subscribe_mass(["ProblemSolver"])
solver.subscribe_mass(["AgentUI"])
"""


def setup_solver():
	solver = CoreProblemSolver(name="ProblemSolver")
	solver.subscribe_mass(["AgentUI"])

def setup_agentui():
	user_agent = UserAgent("AgentUI", analyzer=Analyzer('http://localhost:8090'), 
							specializer=CoreSpecializer(), decoder=NtupleDecoder())
	user_agent.subscribe_mass(["ProblemSolver"])
	user_agent.prompt()

def start(args):
	if "ProblemSolver" in args:
		setup_solver()
		#solver = CoreProblemSolver(name="ProblemSolver")
		#solver.subscribe_mass(["AgentUI"])
	if "AgentUI" in args:
		setup_agentui()

args = sys.argv[1:]
start(args)


"""
while True:
	msg = input("> ")
	if msg == "q":
		quit()
	user_agent.process_input(msg)


"""
