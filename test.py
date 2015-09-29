import json
from robots.morse_solver import *

f = open("manfred.json", "r")

data = json.load(f)

solver = MorseRobotProblemSolver(["ProblemSolver"])

for k, v in data.items():
	print(k)
	new = json.dumps(v)
	solver.solve(new)