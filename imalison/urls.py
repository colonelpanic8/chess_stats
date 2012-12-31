from django.conf.urls import patterns, url
import chess_stats.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
	'',
	url(r'chess_stats/browse_games/.*', chess_stats.views.UserGameBrowserView.as_view()),
	url(r'chess_stats/browse_moves/.*', chess_stats.views.UserMoveBrowserView.as_view()),
	url(r'chess_stats/get_stats/.*', chess_stats.views.get_game_stats)
    # Examples:
    # url(r'^$', 'imalison.views.home', name='home'),
    # url(r'^imalison/', include('imalison.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
