#!/usr/bin/env python
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from chess_stats import tornado

if __name__ == '__main__':
	http_server = HTTPServer(tornado.application)
	http_server.listen(8888)
	IOLoop.instance().start()
