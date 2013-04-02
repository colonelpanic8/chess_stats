from ChessUtil.playable_game import PlayableChessGame
from uci_client import StockfishClient


class ChessGameAnalyzer(object):

	def __enter__(self):
		self.uci_client = StockfishClient()
		return self

	def __init__(self):
		self.uci_client = None

	def yield_move_analyses(self, moves_list):
		playable_game = PlayableChessGame()
		uci_moves = []
		evaluations = []
		for move in moves_list:
			self.uci_client.set_position_from_moves_list(uci_moves)
			evaluations.append(self.uci_client.evaluate_position())
			uci_moves.append(playable_game.make_move_from_algebraic_and_return_uci(move))
			yield move, uci_moves[-1], evaluations[-1]

	def __exit__(self, exc_type, exc_value, traceback):
		try:
			self.uci_client.quit()
		except Exception:
			pass
