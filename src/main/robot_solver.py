"""
A RobotProblemSolver that extends the CoreProblemSolver in the NLUAS module.

Actions, like "move", should be named by predicate + action type.
Thus: query_move, command_move, etc.
Or: query_be, command_be, etc.

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
from math import sqrt

class BasicRobotProblemSolver(CoreProblemSolver):
    def __init__(self, args):
        CoreProblemSolver.__init__(self, args)
        self.headings = dict(north=(0.0, 1.0, 0.0), south=(0.0, -1.0, 0.0), 
                    east=(1.0, 0.0, 0.0), west=(-1.0, 0.0, 0.0))
        self.world = build('mock')
        self._recent = None
        self._wh = None
        # This depends on how size is represented in the grammar.
        self._size_cutoffs = {'big': 2,
                              'small': 1}
        self._home = None
        self._distance_multipliers = {'box': 1.3,
                                    'robot': -.2}
        self._distance_threshold = 4


    def set_home(self, ntuple):
        if ntuple.parameters[0].kind == "cause":
            prot = ntuple.parameters[0].causer
        else:
            prot = ntuple.parameters[0].protagonist
        self._home = self.get_described_object(prot['objectDescriptor']).pos

    def solve_command(self, ntuple):
        self.set_home(ntuple)
        for param in ntuple.parameters:
            self.route_action(param, "command")

    def solve_query(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)


    def command_move(self, parameters):
        information = self.get_move_info(parameters)
        destination = information['destination']
        if destination:
            self.move(information['protagonist'], destination['x'], destination['y'], destination['z'], 
                information['speed'], tolerance=2)
        else:
            print("Command_move, no destination.")
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
            #print(obj)
            if obj:
                destination['x'] = obj.pos.x
                destination['y'] = obj.pos.y
                destination['z'] = obj.pos.z
            else:
                return None
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

    def distance(self, a, b):
        return sqrt(pow((a.pos.x-b.pos.x ),2) + pow((a.pos.y-b.pos.y ),2) ) 

    def get_near(self, candidates, obj):
        locations = []
        for candidate in candidates:
            if self.is_near(candidate, obj):
                locations.append(candidate)
        return locations

    def get_threshold(self, first, second):
        multiplier = self._distance_multipliers[first.type] + self._distance_multipliers[second.type]
        return self._distance_threshold * multiplier

    def is_near(self, first, second):
        """ Could be redone. Essentially an arbitrary threshold. Could be rewritten
        to evaluate "near" in a more relativistic way. 
        Could also take size into account. """
        if first == second:
            return False
        t = self.get_threshold(first, second)
        return self.distance(first, second) <= self.get_threshold(first, second)

    def get_described_locations(self, candidates, description):
        obj = self.get_described_object(description['objectDescriptor'])
        if obj:
            locations = []
            if description['relation'] == 'near':
                locations = self.get_near(candidates, obj)
            elif description['relation'] == 'behind':
                pass
            return locations
        else:
            return []




    def get_described_location(self, candidates, description, multiple=False):
        locations = self.get_described_locations(candidates, description)
        if multiple:
            return locations
        if len(locations) != 1:
            return []
        else:
            return locations[0]

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
        copy = []
        if 'color' in description:
            color = description['color']
            for obj in objs:
                if obj.color == color:
                    copy.append(obj)
            objs = copy


        kind = description['kind']
        if 'size' in description:
            size = description['size']
            objs = self.evaluate_feature(size, kind, objs)

        if 'locationDescriptor' in description:
            #pass
            objs = self.get_described_location(objs, description['locationDescriptor'], multiple=multiple)
            # Get locations...

        return objs



    def get_described_object(self, description, multiple=False):
        objs = self.get_described_objects(description, multiple)
        if len(objs) == 1:
            self._recent = objs[0]
            return objs[0]
        elif len(objs) > 1:
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

    def evaluate_feature(self, feature, kind, objs):
        """ Could probably be generalized to other properties."""
        if kind == "superlative":
            dispatch = getattr(self, "get_{}est".format(feature))
            objs = dispatch(objs)
        elif kind == "comparative":
            pass
            # Do something?
        else:
            dispatch = getattr(self, "get_{}".format(feature))
            objs = dispatch(objs)
        return objs


    def get_big(self, objs):
        bigs = []
        big_cutoff = self._size_cutoffs['big']
        for i in objs:
            if float(i.size) >= big_cutoff:
                bigs.append(i)
        return bigs

    def get_small(self, objs):
        smalls = []
        small_cutoff = self._size_cutoffs['small']
        for i in objs:
            if float(i.size) <= small_cutoff:
                smalls.append(i)
        return smalls

    def get_biggest(self, objs):
        biggest = objs[0]
        returned = [biggest]
        for i in objs:
            if float(i.size) > biggest.size:
                biggest = i
                returned = [biggest]
            elif (float(i.size) == biggest.size) and (i.name != biggest.name):
                returned.append(i)
                # DO SOMETHING HERE ***
        return returned

    def get_smallest(self, objs):
        """ Returns the smallest object of input OBJS. If there are multiple smallest, it returns multiple. """
        smallest = objs[0]
        returned = [smallest]
        for i in objs:
            if float(i.size) < smallest.size:
                smallest = i
                returned = [smallest]
            elif (float(i.size) == smallest.size) and (i.name != smallest.name):
                returned.append(i)
        return returned




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
        print("{} is moving to ({}, {}, {}).".format(mover.name, x, y, z))

if __name__ == "__main__":
    solver = BasicRobotProblemSolver(sys.argv[1:])
    sample = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample2 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'size': 'big', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample3 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'green', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample4 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'blue', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample5 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'size': 'small', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample6 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'pink', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}}}})], predicate_type='command')
    sample7 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'referent': 'robot2_instance', 'type': 'robot'}}}})], predicate_type='command')
