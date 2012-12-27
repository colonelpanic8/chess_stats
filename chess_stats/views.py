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
		# This is a dirty way to do this. Consider using re instead.
		username = self.request.path[13:]
		context['games'] = logic.fetch_games_for_user(username)
		return context
