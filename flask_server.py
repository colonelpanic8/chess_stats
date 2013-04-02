#!/usr/bin/env python
from chess_stats import app
from chess_stats import routes

from util import parse_host_and_port

_pyflakes_ignore = [routes]

if __name__ == "__main__":
	host, port = parse_host_and_port()
	app.port = port
	app.run(port=port, host=host)
