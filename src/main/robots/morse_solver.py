"""
A Morse Problem Solver (extends BasicRobotProblemSolver).

"""

from robot_solver import *
from robot_utils.avoidance import TwoDimensionalAvoidanceSolver

class MorseRobotProblemSolver(BasicRobotProblemSolver, TwoDimensionalAvoidanceSolver):
    def __init__(self, args):
        BasicRobotProblemSolver.__init__(self, args)
        TwoDimensionalAvoidanceSolver.__init__(self)
        self.world = build('morse')

    def move(self, mover, x, y, z=0.0, speed=2, tolerance=3, collide=False):
        if collide:
            new, interrupted = mover.move_np(x=x, y=y, z=z, speed=speed, tolerance=tolerance)
        else:
            origin = [mover.pos.x, mover.pos.y]
            destination = [x, y]  #z?
            line = self.compute_line(origin, destination, mover)
            smoothed = self.smooth_trajectory(line)
            for point in smoothed:
                new, interrupted = mover.move(x=point[0], y=point[1], z=0, speed=speed, tolerance=tolerance)
                if interrupted:
                    self.update_world(agent=mover, discovered=new)
                    self.move(mover, x, y, z, speed, tolerance, collide=False)
        self.update_world(agent=mover)


    def update_world(self, agent, discovered=[]):
        newworld = agent.get_world_info()
        # This will need to be changed dependent on worldview; 
        for obj in newworld:
            if hasattr(self.world, obj['name']):    
                setattr(getattr(self.world, obj['name']), 'pos',Struct(x =obj['position'][0], y=obj['position'][1], z =obj['position'][2]) )
            else:
                #if obj['type'] in discovered:
                print(obj['name'])
                print(discovered)
                if obj['name'] in discovered:
                    print(obj)
                    description = json.loads(obj['description'])
                    self.world.__dict__[obj['name']] = Struct(pos=Struct(x =obj['position'][0], y=obj['position'][1], z = obj['position'][2]), 
                                                              name=obj['name'],
                                                              type=obj['type'],
                                                              color=description['color'],
                                                              size=description['size'])

    def getpos(self, inst):
        instance =getattr(self.world, inst)
        p = instance.pos
        return (p.x, p.y, p.z) 





if __name__ == "__main__":
    solver = MorseRobotProblemSolver(sys.argv[1:])
    sample3 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'green', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample2 = Struct(return_type='error_descriptor', parameters=[Struct(p_features={'voice': 'active'}, kind='cause', causer={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, action='push_move', causalProcess={'p_features': None, 'kind': 'execute', 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, 'action': 'forceapplication', 'acted_upon': {'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'gender': 'genderValues', 'color': 'green', 'type': 'box', 'kind': 'None'}}, 'collaborative': False}, collaborative=False, affectedProcess={'kind': 'execute', 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'gender': 'genderValues', 'color': 'green', 'type': 'box', 'kind': 'None'}}, 'collaborative': False, 'speed': 0.5, 'p_features': None, 'heading': 'north', 'action': 'move'})], predicate_type='command')