from collections import namedtuple
import logging

from .uci_client import StockfishClient
from . import models
from . import logic


TheoreticalWeakness = namedtuple('TheoreticalWeakness', ["line", "optimal", "played", "times_played"])
log = logging.getLogger(__name__)


class TheoreticalHistoryAnalyzer(object):

    def __init__(self, username, min_plays=3, centipawn_threshold=15, as_black=False, shortcircuit=True):
        self.user = models.ChessDotComUser.find_user_by_username(username)
        self._min_plays = min_plays
        self._centipawn_threshold = centipawn_threshold
        self._as_black = as_black
        self._shortcircuit = shortcircuit

    def _find_games_by_moves_string(self, uci_moves_list):
        games_query = self.user.black_games if self._as_black else self.user.white_games
        return games_query.filter(models.ChessDotComGame.uci_moves_string_filter(''.join(uci_moves_list)))

    def analyze(self, engine_client, initial_moves=()):
        games = self._find_games_by_moves_string(initial_moves).all()
        return self._analyze(games, len(initial_moves), engine_client)

    def _user_made_last_move(self, index):
        return self._as_black == (index % 2 == 0)

    def _analyze(self, games, move_index, engine_client):
        weaknesses = []
        if len(games) < self._min_plays:
            raise StopIteration()
        if move_index > 0 and self._user_made_last_move(move_index):
            uci_moves = games[0].uci_moves_list[:move_index]
            weakness = self._find_weakness(uci_moves, engine_client)
            if weakness:
                optimal, played = weakness
                yield TheoreticalWeakness(uci_moves, optimal, played, len(games))
                if self._shortcircuit:
                    raise StopIteration()
        move_to_games = logic.build_next_move_map_at_move_index(games, move_index)
        next_move_index = move_index + 1
        for _, move_games in move_to_games.items():
            for weakness in self._analyze(move_games, next_move_index, engine_client):
                yield weakness

    def _find_weakness(self, uci_moves, engine_client):
        selected_move = uci_moves[-1]
        position = uci_moves[:-1]
        optimal_analysis_info = engine_client.evaluate_position_for(position)
        if optimal_analysis_info.best_move != selected_move:
            played_analysis_info = engine_client.evaluate_position_for(uci_moves)
            if optimal_analysis_info.centipawn_score - (played_analysis_info.centipawn_score * -1) > self._centipawn_threshold:
                print "Weakness found"
                return optimal_analysis_info, played_analysis_info
            else:
                print "Suboptimal move, but not weakness"


class AnalysisAdder(object):

    @staticmethod
    def at_least_n(n):
        def at_least(uci_moves_list):
            return models.ChessDotComGame.query.filter(
                models.ChessDotComGame.uci_moves_list_filter(uci_moves_list)
            ).count() < n
        return at_least

    def __init__(self, termination_condition=None):
        self.termination_condition = termination_condition or self.at_least_n(10)
        self.uci_client = StockfishClient()

    def build_analysis_nodes(self, game):
        with self.uci_client:
            uci_moves = []
            for uci_move in game.uci_moves_list:
                uci_moves.append(uci_move)
                if self.termination_condition(uci_moves):
                    break
                self._build_or_find_analysis_node(uci_moves)

    def _build_or_find_analysis_node(self, uci_moves):
        if models.PositionAnalysis.query.filter(
            models.PositionAnalysis.uci_moves_list_filter(uci_moves)
        ).count() == 0:
            log.debug("Adding node for {0}".format(uci_moves))
            evaluation = self.uci_client.evaluate_position_for(uci_moves, duration=6.5)
            position_analysis = models.PositionAnalysis(moves=''.join(uci_moves),
                                                        centipawn_score=evaluation.centipawn_score,
                                                        best_move_uci=evaluation.best_move)
            models.db.session.add(position_analysis)
            models.db.session.commit()
