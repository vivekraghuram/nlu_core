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
        self._speed = 4
        # This depends on how size is represented in the grammar.
        self._size_cutoffs = {'big': 2,
                              'small': 1}
        self._home = None
        self._distance_multipliers = {'box': 1.3,
                                    'robot': .7}
        self._distance_threshold = 8
        self._attributes = ['size', 'color']


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
        for param in ntuple.parameters:
            self.route_action(param, "query")


    def command_move(self, parameters):
        information = self.get_move_info(parameters)
        destination = information['destination']
        if destination:
            self.move(information['protagonist'], destination['x'], destination['y'], destination['z'], 
                information['speed'], tolerance=2)
        else:
            print("Command_move, no destination.")

    def get_move_info(self, parameters):
        information = dict(destination=None,
                           protagonist=None,
                           speed=None)

        information['protagonist'] = self.get_described_object(parameters.protagonist['objectDescriptor'])
        information['speed'] = parameters.speed * self._speed
        if parameters.goal:
            information['destination'] =self.goal_info(parameters.goal)
        elif parameters.heading:
            information['destination'] = self.heading_info(information['protagonist'], parameters.heading, parameters.distance)
        return information

    def goal_info(self, goal):
        destination = dict(x=None, y=None, z=0.0)
        if "location" in goal:
            if goal['location'] == 'home':
                # Determine "home" position
                destination['x'] = self._home.x
                destination['y'] = self._home.y
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
        elif "locationDescriptor" in goal:
            properties = goal['locationDescriptor']
            position = self.get_described_position(properties)
            destination['x'], destination['y'], destination['z'] = position[0], position[1], position[2]
        return destination

    def getpos(self, inst):
        p = getattr(getattr(self.world, inst), 'pos')
        return (p.x, p.y, p.z) 

    def heading_info(self, protagonist, heading, distance):
        n = float(distance['value'])
        # units?
        name = getattr(protagonist, 'name')
        pos = self.getpos(name)
        newpos = vector_add(pos, vector_mul(n, self.headings[heading]))
        return dict(x=newpos[0], y=newpos[1], z=newpos[2])

    def query_move(self, parameters):
        return None

    def command_push_move(self, parameters):
        #protagonist = self.get_described_object(parameters.causer['objectDescriptor'])
        info = self.get_push_info(parameters)
        if info['goal']:
            # Create self.push_to_location
            self.identification_failure(message=self._incapable)
        elif info['heading']:
            self.push_direction(info['heading'], info['acted_upon'], info['distance'], info['pusher'])


    def push_direction(self, heading, acted_upon, distance, pusher):
        info = self.get_push_direction_info(heading, acted_upon, distance['value'])
        self.move(pusher, info['x1'], info['y1'], tolerance=1.5)
        self.move(pusher, info['x2'], info['y2'], tolerance=2, collide=True)


    def get_push_direction_info(self, heading, obj, distance):
        addpos = vector_mul(-6, self.headings[heading])
        addpos2 = vector_mul(distance, self.headings[heading])
        return {'x1': obj.pos.x + addpos[0], 
                'y1': obj.pos.y + addpos[1],
                'x2': obj.pos.x + addpos2[0],
                'y2': obj.pos.y + addpos2[1]}



    def get_push_info(self, parameters):
        heading = parameters.affectedProcess['heading']
        pusher = self.get_described_object(parameters.causer['objectDescriptor'])
        goal = parameters.affectedProcess['goal']
        distance = parameters.affectedProcess['distance']
        info = dict(goal=None,
                    heading=None,
                    acted_upon=None,
                    distance=None,
                    pusher=None)
        obj = self.get_described_object(parameters.causalProcess['acted_upon']['objectDescriptor'])
        info['acted_upon'] = obj
        if goal:
            info['goal'] = self.goal_info(parameters.affectedProcess['goal'])
        info['heading'] = parameters.affectedProcess['heading'] #self.heading_info(obj, parameters.affectedProcess['heading'], distance)
        info['distance'] = distance
        info['pusher'] = pusher
        return info



    def distance(self, a, b):
        return sqrt(pow((a.pos.x-b.pos.x ),2) + pow((a.pos.y-b.pos.y ),2) ) 

    def get_near(self, candidates, obj):
        locations = []
        for candidate in candidates:
            if self.is_near(candidate, obj):
                locations.append(candidate)
        return locations

    def get_threshold(self, first, second):
        multiplier = (self._distance_multipliers[first.type] * first.size) + (self._distance_multipliers[second.type] * second.size)
        return self._distance_threshold + multiplier

    def is_near(self, first, second):
        """ Could be redone. Essentially an arbitrary threshold. Could be rewritten
        to evaluate "near" in a more relativistic way. 
        Could also take size into account. """
        if first == second:
            return False
        #t = self.get_threshold(first, second)
        #print(t)
        return self.distance(first, second) <= self.get_threshold(first, second)


    def get_described_position(self, description, protagonist):
        """ Returns the position/location described, e.g. "into the room", "near the box".
        (As opposed to an object described in relation to a location.) """
        obj = self.get_described_object(description['objectDescriptor'])
        if description['relation'] == 'behind':
            return self.behind(obj.pos, protagonist.pos)
        else:
            print(properties['relation'])

    def behind(self, position, reference):
        xdiff = position.x - reference.y
        ydiff = position.y - ref.y
        if abs(xdiff) > abs(ydiff):
            if xdiff>0:
                new = [position.x +3, position.y]
            elif xdiff<0:
                new = [position.x -3, position.y]
        elif abs(xdiff) < abs(ydiff):
            if ydiff>0:
                new = [position.x, position.y+3]
            elif ydiff<0:
                new = [position.x , position.y-3]
        elif abs(xdiff) == abs(ydiff):
            if ydiff>0:
                newy =  position.y+3
            elif ydiff<0:
                newy = position.y-3
            if xdiff>0:
                newx =  position.x+3
            elif xdiff<0:
                newx = position.x-3
            new = [newx, newy]
        new.append(0)
        return new




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

        kind = description['kind'] if 'kind' in description else 'unmarked'
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

    def query_be(self, parameters):
        if hasattr(parameters, "specificWh"):
            return self.eval_wh(parameters, self.ntuple.return_type)
        return self.evaluate_condition(parameters)

    def eval_wh(self, parameters, return_type):
        num, referentType = return_type.split("::")
        protagonist = parameters.protagonist
        predication = parameters.predication
        dispatch = getattr(self, "eval_{}".format(parameters.specificWh))
        dispatch(protagonist, predication, num)
        #else:
        #print("Eval_Wh error, no protagonist found.")

    def eval_which(self, protagonist, predication, num):
        description = protagonist['objectDescriptor']
        #description.update(predication)
        copy = []
        objs = self.get_described_objects(description)
        for obj in objs:
            if self.evaluate_obj_predication(obj, predication):
                copy.append(obj)
        if len(copy) > 1:
            if num == "singleton":
                self.identification_failure(message="There is more than one {}.".format(self.assemble_string(description)))
        reply = ""
        for obj in copy:
            reply += "{} \n".format(obj.name)
        self.respond_to_query(message=reply)

    #def evaluate_condition(self):

    def evaluate_obj_predication(self, obj, predication):
        negated = predication['negated']
        #predication
        kind = predication['kind'] if 'kind' in predication else 'unmarked'
        for k, v in predication.items():
            if k == "color":
                if obj.color != v:
                    return negated
            if k == "size":
                # TODO: also incorporate object type??
                if obj.size != self._size_cutoffs[v]:
                    return negated

            if k == "identical":
                pass
                #return self.is_identical(item, prediction['identical']['objectDescriptor'])
            if k == 'relation':
                if v =='near':
                    if !self.is_near(obj, self.get_described_obj(predication['objectDescriptor'])):
                        return negated
            #if k == "size":
            #    if self.evaluate_feature()
            #        return negated
        return True





    # Assertions not yet implemented for robots
    def solve_assertion(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)

    def solve_conditional_imperative(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)

    # Conditional declaratives not yet implemented for robots
    def solve_conditional_declarative(self, ntuple):
        self.decoder.pprint_ntuple(ntuple)


    def move(self, mover, x, y, z=0.0, speed=2, tolerance=2, collide=False):
        print("{} is moving to ({}, {}, {}).".format(mover.name, x, y, z))

if __name__ == "__main__":
    solver = BasicRobotProblemSolver(sys.argv[1:])
    sample = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample2 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'size': 'big', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample3 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'green', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample4 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'blue', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')
    sample5 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'red', 'size': 'small', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}})], predicate_type='command')

    sample6 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'pink', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}}}})], predicate_type='command')
    sample7 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance','size' : 1}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'referent': 'robot2_instance', 'type': 'robot','size' : 1}}}})], predicate_type='command')

    #sample6 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'color': 'green', 'kind': 'None', 'gender': 'genderValues', 'type': 'box'}}}})], predicate_type='command')
    #sample7 = Struct(return_type='error_descriptor', parameters=[Struct(direction=None, action='move', collaborative=False, kind='execute', p_features={'voice': 'notPassive'}, speed=0.5, protagonist={'objectDescriptor': {'type': 'robot', 'referent': 'robot1_instance'}}, control_state='ongoing', goal={'objectDescriptor': {'number': 'singular', 'negated': False, 'givenness': 'uniquelyIdentifiable', 'kind': 'None', 'gender': 'genderValues', 'type': 'box', 'locationDescriptor': {'relation': 'near', 'objectDescriptor': {'referent': 'robot2_instance', 'type': 'robot'}}}})], predicate_type='command')
    sample8 = Struct(predicate_type='command', parameters=[Struct(affectedProcess={'direction': None, 'heading': 'north', 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'negated': False, 'gender': 'genderValues', 'color': 'blue', 'type': 'box', 'kind': 'None', 'number': 'singular', 'givenness': 'uniquelyIdentifiable'}}, 'goal': None, 'action': 'move', 'kind': 'execute', 'speed': 0.5, 'collaborative': False, 'distance': {'units': 'square', 'value': 4}}, collaborative=False, action='push_move', kind='cause', p_features={'voice': 'active'}, causer={'objectDescriptor': {'referent': 'robot1_instance', 'type': 'robot'}}, causalProcess={'direction': None, 'heading': None, 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'referent': 'robot1_instance', 'type': 'robot'}}, 'acted_upon': {'objectDescriptor': {'negated': False, 'gender': 'genderValues', 'color': 'blue', 'type': 'box', 'kind': 'None', 'number': 'singular', 'givenness': 'uniquelyIdentifiable'}}, 'goal': None, 'action': 'forceapplication', 'kind': 'execute', 'speed': 0.5, 'collaborative': False, 'distance': {'units': 'square', 'value': 4}})], return_type='error_descriptor')
    sample9 = Struct(predicate_type='command', parameters=[Struct(affectedProcess={'direction': None, 'heading': None, 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'negated': False, 'gender': 'genderValues', 'color': 'blue', 'type': 'box', 'kind': 'None', 'number': 'singular', 'givenness': 'uniquelyIdentifiable'}}, 'goal': {'objectDescriptor': {'negated': False, 'gender': 'genderValues', 'color': 'green', 'type': 'box', 'kind': 'None', 'number': 'singular', 'givenness': 'uniquelyIdentifiable'}}, 'action': 'move', 'kind': 'execute', 'speed': 0.5, 'collaborative': False, 'distance': {'units': 'square', 'value': 4}}, collaborative=False, action='push_move', kind='cause', p_features={'voice': 'active'}, causer={'objectDescriptor': {'referent': 'robot1_instance', 'type': 'robot'}}, causalProcess={'direction': None, 'heading': None, 'control_state': 'ongoing', 'protagonist': {'objectDescriptor': {'referent': 'robot1_instance', 'type': 'robot'}}, 'acted_upon': {'objectDescriptor': {'negated': False, 'gender': 'genderValues', 'color': 'blue', 'type': 'box', 'kind': 'None', 'number': 'singular', 'givenness': 'uniquelyIdentifiable'}}, 'goal': None, 'action': 'forceapplication', 'kind': 'execute', 'speed': 0.5, 'collaborative': False, 'distance': {'units': 'square', 'value': 4}})], return_type='error_descriptor')
    query1 = Struct(parameters=[Struct(protagonist={'objectDescriptor': {'gender': 'genderValues', 'number': 'singular', 'type': 'box', 'givenness': 'givennessValues'}}, kind='query', specificWh='which', p_features={'tense': 'present'}, predication={'negated': False, 'color': 'big'}, action='be')], predicate_type='query', return_type='singleton::instance_reference')
    query2 = Struct(parameters=[Struct(protagonist={'objectDescriptor': {'gender': 'genderValues', 'number': 'plural', 'type': 'box', 'givenness': 'givennessValues'}}, kind='query', specificWh='which', p_features={'tense': 'present'}, predication={'negated': False, 'color': 'red'}, action='be')], predicate_type='query', return_type='collection_of::instance_reference')
    solver.ntuple = query1

