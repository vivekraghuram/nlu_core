"""
Author: seantrott <seantrott@icsi.berkeley.edu>

"""

from robots.robot_solver import BasicRobotProblemSolver
import sys
import json

class BossSolver(BasicRobotProblemSolver):
    def __init__(self, args):
        BasicRobotProblemSolver.__init__(self, args)
        self.workers = {}
        self.setup_workers()

    def setup_workers(self):
        self.workers['robot1_instance'] = "{}_Robot1".format(self.federation)
        self.workers['robot2_instance'] = "{}_Robot2".format(self.federation)
        for key, value in self.workers.items():
            self.transport.subscribe(value, self.feedback)

    def feedback(self, json_ntuple):
        """ Receiving feedback from workers. """
        print(json_ntuple)

    def callback(self, json_ntuple):
        ntuple = self.decoder.convert_JSON_to_ntuple(json_ntuple)
        predicate_type = ntuple['predicate_type']
        if predicate_type in ['query', 'assertion']:
            self.solve(json_ntuple)
        else:
            self.route(ntuple)

    def route(self, ntuple):
        """ Should actually do this for each parameter. """
        """
        agent_desc = self.identify_agent(ntuple)  
        agent = agent_desc['objectDescriptor']['referent']
        if agent in self.workers:
            destination = self.workers[agent]
            self.transport.send(destination, self.decoder.convert_to_JSON(ntuple))
        """
        for param in ntuple['parameters']:
            agent_desc = self.identify_agent(param)
            if 'referent' in agent_desc['objectDescriptor']:
                agent = agent_desc['objectDescriptor']['referent']
                if agent in self.workers:
                    destination = self.workers[agent]
                    new_ntuple = dict(return_type=ntuple['return_type'],
                                      predicate_type=ntuple['predicate_type'],
                                      parameters=[param])
                    self.transport.send(destination, self.decoder.convert_to_JSON(new_ntuple))



    def identify_agent(self, param):
        if param['kind'] in ['conditional_imperative', "conditional_declarative"]:
            return param['command'][0]['protagonist']
        return param['protagonist']       
        


if __name__ == "__main__":
    boss = BossSolver(sys.argv[1:])