"""
Author: seantrott <seantrott@icsi.berkeley.edu>
"""

from nluas.language.core_specializer import *

filepath = "/Users/seantrott/icsi/nlu-core/src/main/robots/robot_templates.json"

class RobotSpecializer(CoreSpecializer, RobotTemplateSpecializer):
	def __init__(self, analyzer_port):
		CoreSpecializer.__init__(self, analyzer_port)
		RobotTemplateSpecializer.__init__(self)

		self.read_templates(filepath)

		self.simple_processes['Perception'] = self.params_for_perception


	def params_for_perception(self, process, params):
		perceived = self.get_objectDescriptor(process.content)
		params.update(content=perceived)
		return params



