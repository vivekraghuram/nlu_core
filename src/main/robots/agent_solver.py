"""
Author: seantrott <seantrott@icsi.berkeley.edu>

"""

from robots.robot_solver import BasicRobotProblemSolver
import sys

class AgentSolver(BasicRobotProblemSolver):
    def __init__(self, args):
        BasicRobotProblemSolver.__init__(self, args)
        #self.workers = {}
        self.boss_destination = "{}_{}".format(self.federation, "ProblemSolver")
        #self.ui_address = self.boss_destination
        self.transport.subscribe(self.boss_destination, self.callback)
        self.setup_agent()

    def setup_agent(self):
    	for name in self.world:
    		new = name.split("_instance")[0]
    		if new == self.name.lower():
    			self.agent = getattr(self.world, name)


    def callback(self, ntuple):
        self.solve(ntuple)




if __name__ == "__main__":
    solver = AgentSolver(sys.argv[1:])