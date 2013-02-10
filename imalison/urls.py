from django.conf.urls import patterns, url
import chess_stats.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
	'',
	url(
		r'^chess_stats/css/move_browser_styles.css',
		chess_stats.views.CSSView.as_view()
	),
	url(
		r'^chess_stats/js/(?P<path>.*)$',
		'django.views.static.serve',
		{
			'document_root': 'chess_stats/js/',
		}
	),
        url(
		r'^chess_stats/img/(?P<path>.*)$',
		'django.views.static.serve',
		{
			'document_root': 'chess_stats/img/',
		}
	),
        url(
		r'^chess_stats/css/(?P<path>.*)$',
		'django.views.static.serve',
		{
			'document_root': 'chess_stats/css/',
		}
	),
	url(
		r'chess_stats/browse_games/.*',
		chess_stats.views.UserGameBrowserView.as_view()
	),
	url(
		r'chess_stats/browse_moves/.*',
		chess_stats.views.UserMoveBrowserView.as_view()
	),
	url(
		r'chess_stats/get_stats/.*',
		chess_stats.views.get_game_stats
	)
)

