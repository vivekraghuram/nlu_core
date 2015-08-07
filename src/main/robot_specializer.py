from nluas.core_specializer import *

class RobotSpecializer(CoreSpecializer, RobotTemplateSpecializer):
	def __init__(self, analyzer_port):
		CoreSpecializer.__init__(self, analyzer_port)
		RobotTemplateSpecializer.__init__(self)

