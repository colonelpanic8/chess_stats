from chess_game_loader import ChessDotComGameLoader
from scraper import ChessDotComScraper


def save_games(games):
	for game in games:
		game.save()


def fetch_games_for_user(username):
	scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE)
	loader = ChessDotComGameLoader()
	scraper.scrape(username)
	games = [loader.execute(raw_data) for raw_data in scraper.get_pgns()]
	save_games(games)
	return games

