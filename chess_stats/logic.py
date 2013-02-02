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

	try:
		scraper.scrape(username, stop_at_id=stop_at_id)
		games = [loader.execute(raw_data) for raw_data in scraper.get_pgns()]
		save_games(games)
	except IOError:
		pass

	user = models.ChessDotComUser.find_user_by_username(username)
	user.last_scanned_chess_dot_com_game_id = \
		user.most_recently_played_game_in_records.chess_dot_com_id
	user.save()
	return user.all_games


def filter_games_by_moves(games, moves):
	return [game for game in games if game.matches_moves(moves)]


def build_next_move_map_for_moves(games, moves):
	"""Given a move list `moves` and a set of games `games`, construct a mapping
	from single moves following the moves from move list and games that
	feature that move.
	"""
	games = filter_games_by_moves(games, moves)
	moves_map = {}
	move_number = len(moves)
	for game in games:
		if not len(game.moves) > move_number:
			continue
		games_with_same_next_move = moves_map.setdefault(
			game.moves[move_number],
			[]
		)
		games_with_same_next_move.append(game)

	return moves_map


def build_stats_for_games(games):
	white_wins = []
	black_wins = []
	draws = []
	for game in games:
		if game.victor_was_white:
			white_wins.append(game)
		elif game.victor_was_white == None:
			draws.append(game)
		else:
			black_wins.append(game)

	game_count = len(games)
	white_win_count = len(white_wins)
	black_win_count = len(black_wins)
	draw_count = len(draws)

	return dict(
		game_count=game_count,
		white_wins=white_win_count,
		black_wins=black_win_count,
		draws=draw_count,
		white_win_pct=float(white_win_count)/game_count,
		black_win_pct=float(black_win_count)/game_count,
		draw_pct=float(draw_count)/game_count,
		white_average_elo=sum(game.white_elo for game in games)/game_count,
		black_average_elo=sum(game.black_elo for game in games)/game_count,
		white_averge_win_elo=sum(game.white_elo for game in white_wins)/(white_win_count or 1),
		white_average_draw_elo=sum(game.white_elo for game in draws)/(draw_count or 1),
		white_average_loss_elo=sum(game.white_elo for game in black_wins)/(black_win_count or 1),
		black_averge_win_elo=sum(game.black_elo for game in black_wins)/(black_win_count or 1),
		black_average_draw_elo=sum(game.black_elo for game in draws)/(draw_count or 1),
		black_average_loss_elo=sum(game.black_elo for game in white_wins)/(white_win_count or 1),
	)


def build_sorted_game_stats_for_moves(games, moves):
	return sorted(
		(
			(move, build_stats_for_games(game_list))
			for move, game_list in build_next_move_map_for_moves(
				games,
				moves
			).iteritems()
		),
		key=lambda item: item[1]['game_count'],
		reverse=True
	)


def build_sorted_game_stats_for_moves_by_username(username, moves, white=True):
	user = models.ChessDotComUser.find_user_by_username(username)
	games = user.white_games if white else user.black_games
	return build_sorted_game_stats_for_moves(
		games.all(),
		moves
	)


def build_sorted_game_stats_for_moves_for_all_games(moves):
	return build_sorted_game_stats_for_moves(
		models.ChessDotComGame.objects.all(),
		moves
	)
