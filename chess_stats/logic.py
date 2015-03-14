from __future__ import division
import bisect
import os
import re
import logging

from chess_game import parse_long_uci_string

from . import models
from .chess_dot_com_etl import ChessDotComGameETL
from .chess_dot_com_etl import ChessDotComGameFileETL
from .legacy_etl import LegacyGameETL
from .scraper import ChessDotComScraper

log = logging.getLogger(__name__)


def refresh_games(games):
    refreshed_games = [ChessDotComGameETL(game.chess_dot_com_id).execute(force_refresh=True) for game in games]
    models.db.session.commit()
    return refreshed_games


def get_games_for_user(username):
    try:
        user = models.ChessDotComUser.find_user_by_username(username)
    except models.NoResultFound:
        return []
    return user.all_games.all()


def fetch_games_for_user(username, stop_at_latest_id=True, stop_at_id=None, return_all=True):
    if stop_at_latest_id:
        try:
            user = models.ChessDotComUser.find_user_by_username(username)
        except models.NoResultFound:
            pass
        else:
            stop_at_id = user.last_scanned_chess_dot_com_game_id

    scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE, username)

    games = save_games_by_ids(scraper.scrape(stop_at_id=stop_at_id))

    user = models.ChessDotComUser.find_user_by_username(username)
    if games:
        user.last_scanned_chess_dot_com_game_id = max(
            games,
            key=lambda game: game.chess_dot_com_id
        ).chess_dot_com_id

    if return_all:
        return user.all_games.all()
    else:
        return games


def save_games_by_ids(game_ids):
    games = [ChessDotComGameETL(game_id).execute() for game_id in game_ids]
    models.db.session.add_all(games)
    models.db.session.commit()
    return games


def yield_scraped_games(username):
    scraper = ChessDotComScraper(ChessDotComScraper.GAME_TYPE_LIVE, username)
    for game_id in scraper.scrape():
        game = ChessDotComGameETL(game_id).execute()
        models.db.session.add(game)
        models.db.session.commit()
        yield game


def load_games_from_legacy_files_in_directory(directory):
    filename_matcher = re.compile('.*\.xml')
    for directory_path, directory_names, filenames in os.walk(directory):
        for filename in filenames:
            if filename_matcher.match(filename):
                print filename
                load_games_from_legacy_xml(
                    os.path.join(directory_path, filename),
                    os.path.basename(directory_path)
                )


def load_games_from_pgn_files_in_directory(directory):
    filename_matcher = re.compile('.*? - (.*?)\.pgn')
    for directory_path, directory_names, filenames in os.walk(directory):
        for filename in filenames:
            if filename_matcher.match(filename):
                yield ChessDotComGameFileETL(os.path.join(directory_path, filename)).execute()


def load_games_from_legacy_xml(filename, username):
    print 'loading %s for %s' % (filename, username)
    games = LegacyGameETL(filename, username).execute()
    return games


def build_next_move_map_at_move_index(games, move_index):
    """Given a move index `move_index` and a set of games `games`,
    construct a mapping from single moves at the move index to games
    featuring that move.
    """
    moves_map = {}
    for game in games:
        if len(game.uci_moves_list) <= move_index:
            continue
        moves_map.setdefault(game.uci_moves_list[move_index], []).append(game)
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


def build_stats_for_user_games(games, user):
    user_wins = []
    opp_wins = []
    draws = []
    for game in games:
        if game.result_as_int > 0:
            if game.white_user_id == user.id:
                user_wins.append(game)
            else:
                opp_wins.append(game)
        elif game.result_as_int < 0:
            if game.black_user_id == user.id:
                user_wins.append(game)
            else:
                opp_wins.append(game)
        else:
            draws.append(game)

    game_count = len(games)
    user_win_count = len(user_wins)
    opp_win_count = len(opp_wins)
    draw_count = len(draws)

    return dict(
        game_count=game_count,
        user_wins=user_win_count,
        opp_wins=opp_win_count,
        draws=draw_count,
        user_win_pct=float(user_win_count)/game_count,
        opp_win_pct=float(opp_win_count)/game_count,
        draw_pct=float(draw_count)/game_count,
    )


def build_stats_for_games_and_add_move(games, move, base_moves_string):
    stats = build_stats_for_games(games)
    stats['move'] = move
    try:
        analysis = models.PositionAnalysis.query.filter(models.PositionAnalysis.uci_moves_list_filter(base_moves_string+move)).one()
    except models.NoResultFound:
        stats['analysis'] = 'N/A'
    else:
        stats['analysis'] = analysis.centipawn_score
    return stats


def build_sorted_game_stats_at_move_index(games, move_index):
    base_moves_string = ''
    if games:
        base_moves_string = ''.join(games[0].uci_moves_list[:move_index])
    return sorted(
        (
            build_stats_for_games_and_add_move(game_list, move,
                                               base_moves_string)
            for move, game_list in build_next_move_map_at_move_index(
                games,
                move_index
            ).iteritems()
        ),
        key=lambda item: item['game_count'],
        reverse=True
    )


def build_sorted_game_stats_for_moves_by_username(username, moves, white=True):
    user = models.ChessDotComUser.find_user_by_username(username)
    games = user.white_games if white else user.black_games
    games = games.filter(models.ChessDotComGame.uci_moves_string_filter(moves))
    return build_sorted_game_stats_at_move_index(
        games.all(),
        len(parse_long_uci_string(moves))
    )


def build_sorted_game_stats_for_moves_for_all_games(moves):
    return build_sorted_game_stats_at_move_index(
        models.ChessDotComGame.query.all(),
        len(parse_long_uci_string(moves))
    )

def refresh_games_for_usernames(usernames):
    for username in usernames:
        fetch_games_for_user(username)

def refresh_all_users_games():
    for user in models.ChessDotComUser.query.all():
        log.info("Refreshing games for {0}".format(user.username))
        print "Refreshing games for {0}".format(user.username)
        print "Refreshed %d games" % len(fetch_games_for_user(user.username, return_all=False))


def game_length(self, game):
    return len(game.uci_moves_list)


class PartitionGames(object):

    def __init__(self, username, granularity=10, bucket_min=20,
                 min_key='min_elo', max_key='max_elo', sort_function=None):
        self.granularity = granularity
        self.bucket_min = bucket_min
        self.user = models.ChessDotComUser.find_user_by_username(username)
        self.min_key = min_key
        self.max_key = max_key
        self.sort_function = sort_function.__get__(self, type(self)) or self.game_elo

    def game_elo(self, game):
        return game.black_elo if game.white_user_id == self.user.id \
            else game.white_elo

    def partition(self, games=None):
        games = games or self.user.all_games.filter(models.ChessDotComGame.time_control_type == 'blitz').all()
        sorted_games = sorted(games, key=self.sort_function)
        keys = [self.sort_function(game) for game in sorted_games]
        game_buckets = []
        last_bucket_max = keys[0]
        last_index = 0
        while len(sorted_games) > last_index + 1:
            target_max = max(last_bucket_max + self.granularity - 1,
                             keys[min(last_index + self.bucket_min, len(sorted_games) - 1)])
            max_index = bisect.bisect_right(keys, target_max)
            bucket = sorted_games[last_index:max_index]
            game_buckets.append(bucket)
            last_index = max_index
            last_bucket_max = target_max
        return game_buckets

    def partition_and_build_stats(self, games=None):
        bucketed_stats = []
        for game_bucket in self.partition(games):
            min_val = self.sort_function(game_bucket[0])
            max_val = self.sort_function(game_bucket[-1])
            bucketed_stats.append(
                {self.min_key: min_val, self.max_key: max_val,
                 "stats": build_stats_for_user_games(game_bucket, self.user)}
            )
        return bucketed_stats
