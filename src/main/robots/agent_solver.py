from robot_solver import BasicRobotProblemSolver
import sys

class AgentSolver(BasicRobotProblemSolver):
	def __init__(self, args):
		BasicRobotProblemSolver.__init__(self, args)
		#self.workers = {}
		self.subscribe("ProblemSolver", self.callback)

	def callback(self, ntuple):
		self.solve(ntuple)




if __name__ == "__main__":
    boss = AgentSolver(sys.argv[1:])