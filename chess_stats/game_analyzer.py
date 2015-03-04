from collections import namedtuple
import math

from chess_game import ChessGame
from .uci_client import StockfishClient
from . import models
from . import logic


class ChessGameManager(object):

    def __init__(self, game):
        self.game_model = game
        self.playable_game = ChessGame()
        self.move_iterator = iter(self.game_model.moves)
        self.uci_moves = []

    def next(self):
        move = self.move_iterator.next()
        uci_move = self.playable_game.make_move_from_algebraic_and_return_uci(move)
        self.uci_moves.append(uci_move)
        return uci_move, move

    def __iter__(self): return self


TheoreticalWeakness = namedtuple('TheoreticalWeakness', ["line", "optimal", "played", "times_played"])


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



class ChessGameAnalyzer(object):

    def __init__(self, game, cp_continuation_threshold=100):
        self.game = game
        self.cp_continuation_threshold = cp_continuation_threshold
        self.manager = ChessGameManager(self.game)
        self.analysis_nodes = []
        self.continuation_nodes = []
        self.last_analysis_info = None

    @property
    def last_node(self):
        if self.analysis_nodes:
            return self.analysis_nodes[-1]

    def execute(self):
        with StockfishClient() as self.uci_client:
            for uci_move, move in self.manager:
                self.analysis_nodes.append(self.analyze_move())
                yield self.last_node

    def build_continuation_nodes(self, analysis_info):
        last_parent = self.last_node
        moves_list = self.manager.uci_moves[:]
        continuations = analysis_info.continuation_string.split(' ')[:4]
        for index, uci_move in enumerate(continuations):
            moves_list.append(uci_move)
            last_parent = models.AnalysisNode(
                parent=last_parent,
                uci_moves=' '.join(moves_list),
                score=last_parent.score * -1,
                best_move=continuations[index + 1]
            )

    def analyze_move(self):
        if analysis_node: return analysis_node
        self.uci_client.set_position_from_moves_list(self.manager.uci_moves)
        analysis_info = self.uci_client.evaluate_position()
        self.analysis_nodes.append(
            models.AnalysisNode(
                parent=self.last_node,
                score=models.AnalysisScore(analysis_info.centipawn_score),
                uci_moves=' '.join(self.manager.uci_moves),
                best_move=analysis_info.best_move
            )
        )
        if math.fabs(
            self.last_analysis_info.centipawn_score + analysis_info.centipawn_score
        ) < self.cp_continuation_threshold:
            self.build_continuation_nodes(analysis_info)
        return
