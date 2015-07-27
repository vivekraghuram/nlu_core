import sys
from nluas.Transport import Transport

myname = sys.argv[1]
remotename = sys.argv[2]

t = Transport(myname)
t.subscribe(remotename, lambda tuple: print('Got', tuple))

while True:
    t.send(remotename, input())