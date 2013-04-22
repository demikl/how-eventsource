#!/usr/bin/env python
import zmq

ctx = zmq.Context()
srv = ctx.socket(zmq.PULL)
srv.bind("tcp://*:6543")
while True:
 msg = srv.recv()
 print msg
