"""
.. A simple builder for environments, i.e., the objects and robots 
    that are part of a simulation scene.

.. moduleauthor:: Luca Gilardi <lucag@icsi.berkeley.edu>

"""

from nluas.utils import Struct

def build(subsystem):
    """Trivial. Return a Struct whose attributes describe all the
    object in the known 'world'.
    """
    class Worlds(object):
        @staticmethod
        def scene():
            box1_instance=Struct(name='box1_instance', type = 'box',
                                               pos=Struct(x=6.0, y=6.0, z=1.0), color='red', size = 2)
            box2_instance=Struct(name='box2_instance', type = 'box',
                                               pos=Struct(x=-5.0, y=4.0, z=1.0), color='blue', size =2)
            box3_instance=Struct(name='box3_instance', type = 'box',
                                               pos=Struct(x=-2, y=-8, z=1), color='green', size = 2)
            box4_instance=Struct(name='box4_instance', type = 'box',
                                               pos=Struct(x=3, y=-7, z=1), color='red', size =1)
            return Struct(robot1_instance= None, box1_instance=box1_instance,box2_instance=box2_instance,box3_instance=box3_instance, box4_instance=box4_instance)
            

        def morse():
            from robots.morse.simulator import Robot
            from robots.morse.simulator import Box
            robot1_instance=Robot('robot1_instance')
            robot2_instance=Robot('robot2_instance')
            world = Worlds.scene()
            setattr(world, 'robot1_instance', robot1_instance)
            setattr(world, 'robot2_instance', robot2_instance)
            return world

        @staticmethod
        def mock():
            robot1_instance=Struct(name='robot1_instance', pos=Struct(x=0.0, y=0.0, z=0.0), type="robot", size=1)
            robot2_instance=Struct(name='robot2_instance', pos=Struct(x=3.0, y=3.0, z=0.0), type="robot", size=1)
            world = Worlds.scene()
            setattr(world, 'robot1_instance', robot1_instance)
            setattr(world, 'robot2_instance', robot2_instance)
            return world
    return getattr(Worlds, subsystem)()
