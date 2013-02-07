import re
from datetime import datetime

from BeautifulSoup import BeautifulSoup

import etl
import models


class LegacyGameExtractory(etl.Extractor):

	def extract(self, filename):
		with open(filename, 'r') as file:
			return BeautifulSoup(file.read()).findAll(name='game')


class MovesTransformer(etl.Transformer):

	move_matcher = re.compile("(.*?)\|(.*)")

	def transform(self, game):
		moves = []
		try:
			game_string = game['moves']
		except Exception:
			return moves

		move_match = self.move_matcher.match(game_string)
		while move_match:
			moves.append(move_match.group(1))
			game_string = move_match.group(2)
			move_match = self.move_matcher.match(game_string)
		if game_string:
			moves.append(game_string)

		return moves


class GameElementTransformer(etl.Transformer):

	def __init__(self, attribute_name):
		self.attribute_name = attribute_name


class IntegerTransformer(GameElementTransformer):

	def transform(self, game):
		return int(game[self.attribute_name])


class StringTransformer(GameElementTransformer):

	def transform(self, game):
		return game[self.attribute_name]


class EloTransformer(etl.Transformer):

	def __init__(self, white=True):
		self.white = white

	def transform(self, game):
		if (game['color'] == 'White') == self.white:
			# If the color that we are looking for is the same as the users color
			return int(game['elo'])
		else:
			return int(game['oppelo'])


class LegacyUserTransformer(etl.Transformer):

	def __init__(self, white=True):
		self.white = white

	def transform(self, game):
		if (game['color'] == 'White') == self.white:
			# If the color that we are looking for is the same as the users color
			username = game['user']
		else:
			username = game['opponent']

		return models.ChessDotComUser.find_user_by_username(
			username,
			create_if_not_found=True
		)


class ResultTransformer(etl.Transformer):

	RESULT_MAP = {
		'Won': True,
		'Lost': False,
		'Draw': None
	}

	def transform(self, game):
		user_was_winner = self.RESULT_MAP[game['result']]
		user_was_white = game['color'] == 'White'
		if user_was_white is user_was_winner:
			return True
		elif not user_was_white is user_was_winner:
			return False
		return user_was_winner


class DateTransformer(etl.Transformer):

	DATE_FORMAT = '%Y-%m-%d'

	def transform(self, game):
		return datetime.strptime(game['date'], self.DATE_FORMAT).date()


class ChessDotComGameLoader(etl.ModelLoader):

	def load(self, transformed_game):
		if transformed_game['chess_dot_com_id'] <= 0:
			transformed_game['chess_dot_com_id'] = None
			return super(ChessDotComGameLoader, self).load(transformed_game)
		try:
			game = models.ChessDotComGame.objects.get(
				chess_dot_com_id=transformed_game['chess_dot_com_id']
			)
		except models.ChessDotComGame.DoesNotExist:
			# The game doesn't exist so we need to load it.
			return super(ChessDotComGameLoader, self).load(transformed_game)
		else:
			# The game already exists; just return it.
			return game


class LegacyGameETL(etl.ETL):

	extractor = LegacyGameExtractory()

	transformers = {
		'moves': MovesTransformer(),
		'white_user': LegacyUserTransformer(True),
		'black_user': LegacyUserTransformer(False),
		'white_elo': EloTransformer(True),
		'black_elo': EloTransformer(False),
		'date_played': DateTransformer(),
		'victor_was_white': ResultTransformer(),
		'chess_dot_com_id': IntegerTransformer('gameid')
	}

	loader = ChessDotComGameLoader(models.ChessDotComGame)

	def __init__(self, filename, username):
		self.filename = filename
		self.username = username
		self.transformed_games = []

	def extract(self):
		self.games = self.extractor.extract(self.filename)

	def transform(self):
		for game in self.games:
			print game['gameid']
			game['user'] = self.username
			self.transformed_games.append(
				{
					key: transformer.transform(game)
					for key, transformer in self.transformers.iteritems()
				}
			)

	def load(self):
		return [
			self.loader.load(transformed_game) for transformed_game in self.transformed_games
		]
