"""
Simple solver "core". Contains capabilities for unpacking 
a JSON n-tuple, as well as routing this n-tuple based 
on the predicate_type (command, query, assertion, etc.). 
Other general capabilities can be added. The design 
is general enough that the same "unpacking" and "routing" 
method can be used, as long as a new method is written for a given
predicate_type. 

"Route_action" can be called by command/query/assertion methods,
to route each parameter to the task-specific method. E.g., "solve_move",
or "solve_push_move", etc.

<seantrott@icsi.berkeley.edu>

"check_for_clarification" should check ntuple and determine if everything is
specified enough. This implementation will depend on a solver's world model,
but the schematic implementation can be implemented here.

"""

from nluas.ntuple_decoder import *
from nluas.core_agent import *
import random
import sys


class CoreProblemSolver(CoreAgent):

	def __init__(self, args):
		self.ntuple = None
		self.decoder = NtupleDecoder()
		CoreAgent.__init__(self, args)
		self.solver_parser = self.setup_solver_parser()
		args = self.solver_parser.parse_args(self.unknown)
		self.complexity = args.complexity
		self.ui_address = "{}_{}".format(self.federation, "AgentUI")
		self.transport.subscribe(self.ui_address, self.callback)

	def setup_solver_parser(self):
		parser = argparse.ArgumentParser()
		parser.add_argument("-c", "--complexity", type=str, help="indicate level of complexity")
		return parser

	def callback(self, ntuple):
		self.solve(ntuple)

	def clarify(self, ntuple):
		new = self.decoder.convert_to_JSON(ntuple)
		self.transport.send(self.ui_address, new)

	def solve(self, json_ntuple):
		ntuple = self.decoder.convert_JSON_to_ntuple(json_ntuple)
		if self.check_for_clarification(ntuple):
			self.clarify(ntuple=ntuple)
		else:
			predicate_type = ntuple.predicate_type
			try:
				dispatch = getattr(self, "solve_%s" %predicate_type)
				dispatch(ntuple)
			except AttributeError:
				print("I cannot solve a(n) {}.".format(predicate_type))

	def solve_command(self, ntuple):
		self.decoder.pprint_ntuple(ntuple)

	def solve_query(self, ntuple):
		self.decoder.pprint_ntuple(ntuple)

	def solve_assertion(self, ntuple):
		self.decoder.pprint_ntuple(ntuple)

	def solve_conditional_imperative(self, ntuple):
		self.decoder.pprint_ntuple(ntuple)

	def solve_conditional_declarative(self, ntuple):
		self.decoder.pprint_ntuple(ntuple)
		

	def route_action(self, parameters):
		action = parameters.action
		try:
			dispatch = getattr(self, "solve_%s"%action)
			dispatch(parameters)
		except AttributeError:
			print("I cannot solve the '{}' action".format(action))

	def close(self):
		return

	def check_for_clarification(self, ntuple):
		""" Will need to be replaced by a process that checks whether ntuple needs clarification.
		Requires some sort of context/world model. """
		#return random.choice([True, False])
		return False

if __name__ == '__main__':
	ps = CoreProblemSolver(sys.argv[1:])
