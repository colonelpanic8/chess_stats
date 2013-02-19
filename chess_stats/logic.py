import os
import re
import simplejson

import models
from chess_dot_com_etl import ChessDotComGameETL
from legacy_etl import LegacyGameETL
from scraper import ChessDotComScraper, ChessComPGNFileFinder


def get_games_for_user(username):
	try:
		user = models.ChessDotComUser.find_user_by_username(username)
	except models.NoResultFound:
		return []
	return user.all_games


def fetch_games_for_user(username, stop_at_latest_id=True, stop_at_id=None):
	if stop_at_latest_id:
		try:
			user = models.ChessDotComUser.find_user_by_username(username)
		except models.NoResultFound:
			pass
		else:
			stop_at_id = user.last_scanned_chess_dot_com_game_id

	scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE, username)

	games = [ChessDotComGameETL(game_id).execute() for game_id in scraper.scrape(stop_at_id=stop_at_id)]

	models.db.session.add_all(games)
	models.db.session.commit()

	user = models.ChessDotComUser.find_user_by_username(username)
	if games:
		user.last_scanned_chess_dot_com_game_id = max(
			games,
			key=lambda game: game.chess_dot_com_id
		).chess_dot_com_id

	return user.all_games.all()


def yield_scraped_games(username):
	scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE, username)
	for game_id in scraper.scrape():
		yield ChessDotComGameETL(game_id).execute()


def load_games_from_legacy_files_in_directory(directory):
	filename_matcher = re.compile('.*\.xml')
	for directory_path, directory_names, filenames in os.walk(directory):
		for filename in filenames:
			if filename_matcher.match(filename):
				load_games_from_legacy_xml(
					os.path.join(directory_path, filename),
					os.path.basename(directory_path)
				)


def load_games_from_legacy_xml(filename, username):
	print 'loading %s for %s' % (filename, username)
	games = LegacyGameETL(filename, username).execute()
	save_games(games)
	return games


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
		if game.result_as_int > 0:
			white_wins.append(game)
		elif game.result_as_int < 0:
			black_wins.append(game)
		else:
			draws.append(game)

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


def build_stats_for_games_and_add_move(games, move):
	stats = build_stats_for_games(games)
	stats['move'] = move
	return stats


def build_sorted_game_stats_for_moves(games, moves):
	return sorted(
		(
			build_stats_for_games_and_add_move(game_list, move)
			for move, game_list in build_next_move_map_for_moves(
				games,
				moves
			).iteritems()
		),
		key=lambda item: item['game_count'],
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
		models.ChessDotComGame.query.all(),
		moves
	)


def get_color_dictionary():
	with open('chess_stats/config/colors.json') as colors_file:
		return simplejson.loads(colors_file.read())
