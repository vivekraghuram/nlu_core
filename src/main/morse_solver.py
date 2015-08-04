"""
A Morse Problem Solver (extends BasicRobotProblemSolver).

"""

from robot_solver import *

class MorseRobotProblemSolver(BasicRobotProblemSolver):
    def __init__(self, args):
        BasicRobotProblemSolver.__init__(self, args)
        self.world = build('morse')


    def move(self, mover, x, y, z, speed, tolerance=2):
        mover.move(x=x, y=y, z=z, speed=speed, tolerance=tolerance)

if __name__ == "__main__":
    solver = MorseRobotProblemSolver(sys.argv[1:])
    sample3 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'green', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
