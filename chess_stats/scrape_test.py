from chess_stats import scraper, chess_game_loader

def do_test():
	s = scraper.ChessComScraper(scraper.ChessComScraper.GAME_TYPE_LIVE)
	s.scrape('IvanMalison')
	pgn = s.get_pgns().next()[2]
	game = chess_game_loader.ChessDotComGameLoader().execute(pgn)
	game.save()
