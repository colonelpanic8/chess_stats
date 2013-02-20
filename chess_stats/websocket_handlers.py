import inspect

import functools
import simplejson
from tornado import websocket

from . import logic


class HandlerRegistrar(type):

	def __init__(self, *args, **kwargs):
		self.request_type_to_funtion_names_map = {}
		for attr_name, attr in inspect.getmembers(self):
			request_type = getattr(attr, 'request_type', False)
			print attr_name,
			print request_type
			if request_type:
				self.request_type_to_funtion_names_map.setdefault(
					request_type,
					[]
				).append(attr_name)
		super(HandlerRegistrar, self).__init__(*args, **kwargs)

	@classmethod
	def register_request_handler(cls, function, request_type):
		function.request_type = request_type
		return function

	@classmethod
	def register_request_handler_decorator(cls, request_type):
		return functools.partial(
			cls.register_request_handler,
			request_type=request_type
		)


class GameFetchHandler(websocket.WebSocketHandler):

	__metaclass__ = HandlerRegistrar

	def __init__(self, *args, **kwargs):
		self.request_type_to_handler_functions_map = {
			request_type: [
				getattr(self, function_name) for function_name in function_names
			]
			for request_type, function_names
			in self.request_type_to_funtion_names_map.iteritems()
		}
		super(GameFetchHandler, self).__init__(*args, **kwargs)

	def open(self):
		self.write_as_json({'type': 'START'})

	def on_message(self, message):
		request = simplejson.loads(message)

		try:
			request_type = request['type']
		except KeyError:
			print "Request did not have type."
			return

		try:
			request_functions = self.request_type_to_handler_functions_map[
				request_type
			]
		except KeyError:
			print "The request type was not recognized."
			return

		for function in request_functions:
			function(request)

	def on_close(self):
		pass

	@HandlerRegistrar.register_request_handler_decorator('GET_GAMES')
	def send_games_one_by_one(self, request):
		for game in logic.yield_scraped_games(request['username']):
			self.write_as_json({'type': "GAME", 'game': game.as_dict})

	def write_as_json(self, obj):
		self.write_message(simplejson.dumps(obj))
