import models
from loader import ChessDotComGameLoader
from scraper import ChessDotComScraper


def save_games(games):
	# TODO: Do this in a single transaction.
	for game in games:
		game.save()


def fetch_games_for_user(username, stop_at_latest_id=True, stop_at_id=None):
	if stop_at_latest_id:
		try:
			user = models.ChessDotComUser.find_user_by_username(username)
		except models.ChessDotComUser.DoesNotExist:
			pass
		else:
			stop_at_id = user.last_scanned_chess_dot_com_game_id

	scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE)
	loader = ChessDotComGameLoader()

	scraper.scrape(username, stop_at_id=stop_at_id)

	games = [loader.execute(raw_data) for raw_data in scraper.get_pgns()]
	save_games(games)

	user = models.ChessDotComUser.find_user_by_username(username)
	user.last_scanned_chess_dot_com_game_id = \
		user.most_recently_played_game_in_records.chess_dot_com_id
	user.save()
	return user.all_games
