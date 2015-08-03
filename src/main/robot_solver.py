"""
A RobotProblemSolver that extends the CoreProblemSolver in the NLUAS module.

Questions:
(1) Keep in mind: should we route based on actions? E.g., "move to the blue box?"
This was how it was done previously, but what about queries/assertions: "he moved to the blue box",
"can you move to the blue box?", "which box did you move?"

Possible solutions:
(1) Separate "information" functions like gathering information from an n-tuple and matching to world,
from action/query functions. Thus, we'd have several functions involving "move", including:
-"do_move"
-"move_info": gather information (used in do_move)

"""

from nluas.core_solver import *
from nluas.utils import *
from robots.builder import *
import sys
import random

class BasicRobotProblemSolver(CoreProblemSolver):
    def __init__(self, args):
        CoreProblemSolver.__init__(self, args)
        self.headings = dict(north=(0.0, 1.0, 0.0), south=(0.0, -1.0, 0.0), 
                    east=(1.0, 0.0, 0.0), west=(-1.0, 0.0, 0.0))
        self.world = build('mock')
        self._recent = None
        self._wh = None


    def solve_command(self, ntuple):
        for param in ntuple.parameters:
            self.route_action(param, "command")

    def solve_query(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)


    def command_move(self, parameters):
        information = self.get_move_info(parameters)
        destination = information['destination']
        self.move(information['protagonist'], destination['x'], destination['y'], destination['z'], 
            information['speed'], tolerance=2)
        #return None


    def get_move_info(self, parameters):
        information = dict(destination=None,
                           protagonist=None,
                           speed=None)

        information['protagonist'] = self.get_described_object(parameters.protagonist['objectDescriptor'])
        information['speed'] = parameters.speed * 4
        if parameters.goal:
            information['destination'] =self.goal_info(information['protagonist'], parameters.goal)
        elif parameters.heading:
            information['destination'] = self.heading_info(information['protagonist'], parameters)
        return information

    def goal_info(self, protagonist, goal):
        destination = dict(x=None, y=None, z=None)
        if "location" in goal:
            if goal['location'] == 'home':
                # Determine "home" position
                pass
            else:
                destination['x'] = goal['location'][0]
                destination['y'] = goal['location'][1]
                # Z point?
                #destination['z'] = goal['location'][0]
        elif 'objectDescriptor' in goal:
            obj = self.get_described_object(goal['objectDescriptor'], multiple=True)
            if obj:
                destination['x'] = obj.pos.x
                destination['y'] = obj.pos.y
                destination['z'] = obj.pos.z
        return destination

    def heading_info(self, protagonist, parameters):
        n = float(parameters.distance['value'])
        # units?
        name = getattr(protagonist, 'name')
        pos = self.getpos(name)
        newpos = vector_add(pos, vector_mul(n, self.headings[heading]))
        return dict(x=newpos[0], y=newpos[1], z=newpos[2])



    def query_move(self, parameters):
        return None

    def get_described_objects(self, description, multiple=False):
        if 'referent' in description:
            if hasattr(self.world, description['referent']):
                return [getattr(self.world, description['referent'])]
            else:
                return []

        obj_type = description['type']
        objs = []
        for item in self.world.__dict__.keys():
            if hasattr(getattr(self.world, item), 'type') and getattr(getattr(self.world, item), 'type') == obj_type:
                objs += [getattr(self.world, item)]
        
        if 'color' in description:
            color = description['color']
            for obj in objs:
                if obj.color!=color:
                    print(obj.color)
                    objs.remove(obj)

        #kind = description['kind']
        #if 'size' in description:
        #    size = description['size']


        return objs




    def get_described_object(self, description, multiple=False):
        objs = self.get_described_objects(description, multiple)
        if len(objs) == 1:
            self._recent = objs[0]
            return objs[0]
        elif len(objs) > 1:
            print("here")
            if "givenness" in description:
                if description['givenness'] == 'typeIdentifiable' or description['givenness'] == "distinct":
                    if self._recent in objs:
                        objs.remove(self._recent)
                    return random.choice(objs)
            elif self._wh:
                message = "More than one object matches the description of {}.".format(self.assemble_string(description))
                self.identification_failure(message)
                return None
            message = "which {}?".format(self.assemble_string(description))
            self.request_clarification(self.ntuple, message)
            return None
        else:
            message = "Sorry, I don't know what the {} is.".format(self.assemble_string(description))
            self.identification_failure(message)
            return None

    def assemble_string(self, properties):
        """ Takes in properties and assembles a string, to format: "which blue box", etc. """
        ont = properties['type']
        attributes = ""
        for key, value in properties.items():   # Creates string of properties
            if key == "referent":
                return value
            if key == "color" or key == "size":
                attributes += " " + value 
            if key == "location":
                attributes += " "  + value
            elif key == "locationDescriptor":
                attributes += " " + str(ont) + " " + value["relation"] + " the " + self.assemble_string(value['objectDescriptor'])
                return attributes
        return str(attributes) + " " + str(ont)

    # Assertions not yet implemented for robots
    def solve_assertion(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)

    def solve_conditional_imperative(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)

    # Conditional declaratives not yet implemented for robots
    def solve_conditional_declarative(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)


    def move(self, mover, x, y, z, speed, tolerance=2):
        print(mover)
        print(x)
        print(y)

if __name__ == "__main__":
    solver = BasicRobotProblemSolver(sys.argv[1:])
    sample = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
