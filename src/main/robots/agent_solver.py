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


    def callback(self, ntuple):
        self.solve(ntuple)




if __name__ == "__main__":
    solver = AgentSolver(sys.argv[1:])