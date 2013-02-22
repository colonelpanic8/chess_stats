#!/usr/bin/env python
import os

from chess_stats import app
from chess_stats import routes

from util import parse_host_and_port
from websocket_server import start_tornado_server

if __name__ == "__main__":
	host, port = parse_host_and_port()
	app.port = port
	app.run(port=port, host=host)
