#!/usr/bin/env python
import itertools
import time
from flask import Flask, Response, redirect, request, url_for
import zmq

app = Flask(__name__)

@app.route('/')
def index():
    if request.headers.get('accept') == 'text/event-stream':
        ctx = zmq.Context()
        srv = ctx.socket(zmq.PULL)
        srv.bind("tcp://*:6543")
        def events():
            while True:
                print "Waiting msg from socket..."
                msg = srv.recv()
                whatToSend = "event: teleinfo\ndata: %s\n\n" % msg
                print whatToSend
                yield whatToSend 

        return Response(events(), content_type='text/event-stream')
    return redirect(url_for('static', filename='index.html'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=23423, debug=True)
