import re
import simplejson

from django.http import HttpResponse
from django.views.generic import TemplateView

import logic


class UserGameBrowserView(TemplateView):
	template_name = (
		'/Users/imalison/Dropbox/Python/imalison/chess_stats/'
		'templates/browse_games.html'
	)

	username_matcher = re.compile('([^/]*?)$')

	def get_context_data(self, **kwargs):
		context = super(UserGameBrowserView, self).get_context_data(**kwargs)
		username = self.username_matcher.search(self.request.path).group(1)
		context['games'] = logic.fetch_games_for_user(username)
		return context


class UserMoveBrowserView(TemplateView):
	template_name = (
		'/Users/imalison/Dropbox/Python/imalison/chess_stats/'
		'templates/browse_moves.html'
	)


def get_game_stats(request):
	username = request.GET['username']
	moves = request.GET.getlist('moves[]')
	return HttpResponse(
		simplejson.dumps(
			logic.build_sorted_game_stats_for_moves_by_username(username, moves)
		)
	)
