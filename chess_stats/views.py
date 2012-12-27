# Create your views here
from django.views.generic import TemplateView

import logic


class UserGameView(TemplateView):
	template_name = (
		'/Users/imalison/Dropbox/Python/imalison/chess_stats/'
		'templates/user_game.html'
	)

	def get_context_data(self, **kwargs):
		context = super(UserGameView, self).get_context_data(**kwargs)
		context['params']['games'] = [
			game for game in logic.fetch_games_for_user('AlexMalison')
		]
		return context

	def prepare_game(self, game):
		game_dict =  {
			attr: getattr(game, attr)
			for attr in game.__class__._meta.get_all_field_names()
		}
		game_dict['black_username'] = game.black_username
		game_dict['white_username'] = game.white_username
		return game_dict
