import math

from ChessUtil.playable_game import PlayableChessGame
from .uci_client import StockfishClient
from . import models


class ChessGameManager(object):

    def __init__(self, game):
        self.game_model = game
        self.playable_game = PlayableChessGame()
        self.move_iterator = iter(self.game_model.moves)
        self.uci_moves = []

    def next(self):
        move = self.move_iterator.next()
        uci_move = self.playable_game.make_move_from_algebraic_and_return_uci(move)
        self.uci_moves.append(uci_move)
        return uci_move, move

    def __iter__(self): return self


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
        analysis_node = models.AnalysisNode.find_from_uci_moves_list(self.manager.uci_moves)
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