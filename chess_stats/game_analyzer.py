from ChessUtil.playable_game import playable_game
from uci_client import StockfishClient


class ChessGameAnalyzer(object):

	def __init__(self):
		self.uci_client = StockfishClient()

	def analyze_moves(self, moves_list):
		pg = playable_game.PlayableChessGame()
		uci_moves = []
		evaluations = []
		for move in moves_list:
			uci_moves.append(pg.make_move_from_algebraic_and_return_uci(move))
			self.uci_client.set_position_from_moves_list(uci_moves)
			evaluations.append(self.uci_client.evaluate_position())
			print uci_moves[-1]
			print evaluations[-1]
		return evaluations

	def close(self):
		self.uci_client.quit()
