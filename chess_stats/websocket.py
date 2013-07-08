from __future__ import absolute_import
import inspect
import functools
import time
import threading

import simplejson
from tornado import websocket

from . import logic
from . import uci_client


class MessageHandlerRegistrar(type):

    def __init__(self, *args, **kwargs):
        self.request_type_to_function_names_map = {}
        for attr_name, attr in inspect.getmembers(self):
            request_type = getattr(attr, 'request_type', False)
            if request_type:
                self.request_type_to_function_names_map.setdefault(
                    request_type,
                    []
                ).append(attr_name)
        super(MessageHandlerRegistrar, self).__init__(*args, **kwargs)

    @classmethod
    def register_request_handler(cls, function, request_type):
        function.request_type = request_type
        return function

    @classmethod
    def register_request_handler_decorator(cls, request_type):
        return functools.partial(cls.register_request_handler, request_type=request_type)


class UnrecognizedMessage(Exception): pass


class MessageHandler(websocket.WebSocketHandler):

    __metaclass__ = MessageHandlerRegistrar

    def on_message(self, message):
        request = simplejson.loads(message)

        try:
            request_type = request['type']
        except KeyError:
            raise UnrecognizedMessage("Message did not have type.")

        try:
           request_function_names = self.request_type_to_function_names_map[
              request_type
           ]
        except KeyError:
            print "The request type was not recognized."
            return

        for function_name in request_function_names:
            getattr(self, function_name)(request)

    def on_close(self):
        pass

    def write_as_json(self, obj):
        self.write_message(simplejson.dumps(obj))


class GameAnalysisHandler(MessageHandler):

    def __init__(self, *args, **kwargs):
        super(GameAnalysisHandler,self).__init__(*args, **kwargs)
        self.uci_client = uci_client.StockfishClient()
        self.engine_manager = self.get_engine_manager()
        self.engine_manager.next()

    def on_close(self):
        try:
            self.engine_manager.next()
        except Exception:
            pass

    def get_engine_manager(self):
        with self.uci_client:
            yield

    @MessageHandlerRegistrar.register_request_handler_decorator('SET_POSITION')
    def set_position(self, request):
        self.uci_client.set_position_from_moves_list(request['uci_moves'])

    @MessageHandlerRegistrar.register_request_handler_decorator('DO_ANALYSIS')
    def do_analysis(self, request):
        self.uci_client.start_position_evaluation()
        time.sleep(5)
        self.write_as_json(
            {
                'type': 'ANALYSIS',
                'analysis': self.uci_client.maybe_read_evaluation()
            }
        )


class GameFetchHandler(MessageHandler):

    @MessageHandlerRegistrar.register_request_handler_decorator('GET_GAMES')
    def send_games_one_by_one(self, request):
        for game in logic.yield_scraped_games(request['username']):
            try:
                self.write_as_json({'type': "GAME", 'game': game.as_dict})
            except IOError:
                print "Stopped sending games because connection was closed."
                return
