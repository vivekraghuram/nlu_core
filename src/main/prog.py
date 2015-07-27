from nluas.core_solver import *
#core = CoreAgent(args.name, federation, args.logfile, args.loglevel, args.logagent)
#core = CoreAgent(args.name, federation, args.logfile, args.loglevel, args.logagent)
core = CoreProblemSolver(sys.argv[1:])

