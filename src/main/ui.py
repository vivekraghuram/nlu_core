from nluas.user_agent import UserAgent
import sys
core = UserAgent(sys.argv[1:])
while True:
	core.prompt()