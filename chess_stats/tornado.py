from __future__ import absolute_import

from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer

from . import app
from . import routes
from . import websocket


tr = WSGIContainer(app)
application = Application(
    [
        (r'/analysis/', websocket.GameAnalysisHandler),
        (r'/fetch_games/', websocket.GameFetchHandler),
        (r".*", FallbackHandler, dict(fallback=tr)),
    ],
    auto_reload=True
)
