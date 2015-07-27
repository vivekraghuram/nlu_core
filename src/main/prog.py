from nluas.core_agent import *
from nluas.core_solver import *
federation = os.environ.get("ECG_FED")
if federation is None:
	federation = "FED1"
#core = CoreAgent(args.name, federation, args.logfile, args.loglevel, args.logagent)
core = CoreProblemSolver(args.name, federation, args.logfile, args.loglevel, args.logagent, args.complexity)
