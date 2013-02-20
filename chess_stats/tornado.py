from __future__ import absolute_import

from tornado.web import Application

from . import websocket


application = Application(
	[(r'/fetch_games/', websocket.GameFetchHandler)],
	auto_reload=True
)
