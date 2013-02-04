import os
import re
import simplejson

from django.http import HttpResponse
from django.views.generic import TemplateView

import logic


username_matcher = re.compile('([^/]*?)$')


class UserGameBrowserView(TemplateView):
	template_name = (os.path.dirname(__file__) + '/templates/browse_games.html')

	def get_context_data(self, **kwargs):
		context = super(UserGameBrowserView, self).get_context_data(**kwargs)
		username = username_matcher.search(self.request.path).group(1)
		context['games'] = logic.fetch_games_for_user(username)
		context['username'] = username
		return context


class UserMoveBrowserView(TemplateView):
	template_name = (os.path.dirname(__file__) + '/templates/browse_moves.html')

	def get_context_data(self, **kwargs):
		context = super(UserMoveBrowserView, self).get_context_data(**kwargs)
		username = username_matcher.search(self.request.path).group(1)
		context['username'] = username
		return context


class CSSView(TemplateView):
	template_name = (os.path.dirname(__file__) + '/css/move_browser_styles.css')

	def get_context_data(self, **kwargs):
		context = super(CSSView, self).get_context_data(**kwargs)
		context.update(logic.get_color_dictionary())
		return context


def get_game_stats(request):
	username = request.GET['username']
	moves = simplejson.loads(request.GET['moves'])
	if username:
		move_stats = logic.build_sorted_game_stats_for_moves_by_username(
			username,
			moves
		)
	else:
		move_stats = logic.build_sorted_game_stats_for_moves_for_all_games(moves)
	json = simplejson.dumps(move_stats)
	return HttpResponse(json)
