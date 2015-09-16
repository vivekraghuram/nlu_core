from robot_solver import BasicRobotProblemSolver
import sys

class BossSolver(BasicRobotProblemSolver):
	def __init__(self, args):
		BasicRobotProblemSolver.__init__(self, args)
		self.workers = {}

	def setup_workers(self):
		self.workers['robot1_instance'] = "{}_Robot1".format(self.federation)
		self.workers['robot2_instance'] = "{}_Robot2".format(self.federation)
		for key, value in self.workers.items():
			self.transport.subscribe(value, self.callback)

	def callback(self, json_ntuple):
		ntuple = self.decoder.convert_JSON_to_ntuple(json_ntuple)
		predicate_type = ntuple['predicate_type']
		if predicate_type == "query":
			self.solve(json_ntuple)
		else:
			self.route(ntuple)

	def route(self, ntuple):
		agent = self.identify_agent(ntuple)		

	def identify_agent(self, ntuple):
		predicate_type = ntuple['predicate_type']
		


if __name__ == "__main__":
    boss = BossSolver(sys.argv[1:])