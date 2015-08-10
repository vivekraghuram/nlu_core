from nluas.core_agent import *
from pyre import Pyre

name = sys.argv[1]
subscribe = "FED1_{}".format(sys.argv[2])

ca = CoreAgent([name])

def callback(message):
	print(message)

ca.transport.subscribe(subscribe, callback)





#ca.transport.quit_federation()
#ca.quitter = Transport("GLOBAL")

#p = Pyre(sys.argv[1])
#ca.quitter.subscribe_all(test)

#ca.transport.subscribe("GLOBAL", test)
#ca.transport.send("GLOBAL", "QUIT")