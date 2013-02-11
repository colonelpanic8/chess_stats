import simplejson
from django_socketio import events

import logic


request_string_to_function_map = {}


def register_request_string_for_function(request_string):
	def decorator(function):
		request_string_to_function_map[request_string] = function
		return function
	return decorator


@events.on_message
def handle_request(request, socket, context, message):
	request_data = simplejson.loads(message)
	import ipdb; ipdb.set_trace()
	try:
		request_string = request_data['request']
	except KeyError:
		# TODO: error handling
		print "No request."
	try:
		print request_string
		request_string_to_function_map[request_string](
			request,
			socket,
			context,
			request_data
		)
	except KeyError:
		# TODO: error handling
		print "No function."


@register_request_string_for_function("GET_GAMES")
def get_games(request, socket, context, request_data):
	for game in logic.yield_scraped_games(request_data["username"]):
		socket.send(game.as_json)
		import ipdb; ipdb.set_trace()
