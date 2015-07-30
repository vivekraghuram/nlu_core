from nluas.user_agent import *
import sys
connected = False
while not connected:
	try:
		core = UserAgent(sys.argv[1:])
		connected = True
	except WaitingException as e:
		pass
		#print(e)
while True:
	core.prompt()