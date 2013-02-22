#!/usr/bin/env python
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from util import parse_host_and_port
from chess_stats import tornado

def start_tornado_server(host, port):
	http_server = HTTPServer(tornado.application)
	http_server.listen(port)
	IOLoop.instance().start()

if __name__ == '__main__':
	host, port = parse_host_and_port()
	tornado.app.port = port
	start_tornado_server(host, port)
