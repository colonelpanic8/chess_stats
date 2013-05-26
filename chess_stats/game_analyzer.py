from ChessUtil.playable_game import PlayableChessGame
from uci_client import StockfishClient


class ChessGameManager(object):

    def __init__(self, game):
        self.game = game
        self.uci_moves = []

    def replay_game(self):
        playable_game = PlayableChessGame()
        for move in self.game.moves:
            uci_move = playable_game.make_move_from_algebraic_and_return_uci(move)
            self.uci_moves.append(uci_move)
            yield uci_move, move


class ChessGameAnalyzer(object):

    def __init__(self, game):
        self.uci_client = None
        self.game = game

    def __enter__(self):
        self.uci_client = StockfishClient()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.uci_client.quit()
        except Exception:
            pass

    def yield_move_analyses(self):
        evaluations = []
        manager = ChessGameManager(self.game)
        for uci_move, move in manager.replay_game():
            self.uci_client.set_position_from_moves_list(manager.uci_moves)
            evaluations.append(self.uci_client.evaluate_position())
            yield move, uci_move, evaluations[-1]
