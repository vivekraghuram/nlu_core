#!/usr/bin/env python
#
# Minimal two-way chat example using Transport.
#
# In shell1: chat.py chat1 chat2
# In shell2: chat.py chat2 chat1
#
# This example also exits correctly.

import select
import sys

from nluas import Transport

myname = sys.argv[1]
remotename = sys.argv[2]

def echo_callback(ntuple, **kw):
    print('%s got %s from %s'%(myname, ntuple, kw['name']))

t = Transport.Transport(myname)
t.subscribe(remotename, echo_callback)

while t.is_running():
    # Wait for input with a 1 second timeout.
    si,so,se = select.select([sys.stdin], [], [], 1)
    if si:
        # Didn't time out. Get input line.
        s = input()
        # If the Transport died while in the input, quit
        if not t.is_running():
            break
        # If the user typed QUIT, stop the federation and quit.
        if s == 'QUIT':
            t.quit_federation()
            break
        # Otherwise send on the message
        t.send(remotename, s)
