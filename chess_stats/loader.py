import re

import etl
import models


class DataError(Exception):
	pass


class MovesExtractor(etl.Extractor):

	def extract(self, pgn_string):
		game_match = re.search(
			"^(1\..*)",
			pgn_string,
			flags=re.DOTALL | re.MULTILINE
		)
		if not game_match:
			return ''
		return game_match.group(1)


class MetaDataExtractor(etl.Extractor):

	META_DATA_FORMAT = '\[{attribute_name} "(.*?)"\]'

	def __init__(self, attribute_name):
		self.attribute_name = attribute_name

	@property
	def match_string(self):
		return self.META_DATA_FORMAT.format(attribute_name=self.attribute_name)

	def extract(self, pgn_string):
		match = re.search(self.match_string, pgn_string)
		if match:
 			return match.group(1)
		raise DataError()


class MovesTransformer(etl.SingleElementTransformer):

	transform_arguments = set(['moves_string'])
	return_names = set(['moves'])

	def _transform(self, moves_string=None):
		moves_string = moves_string.replace('\r\n', '')

		moves = []
		move_match = re.match(
			"[0-9]*?\.(.*?) (.*?) (.*)",
			moves_string,
			flags=re.DOTALL | re.MULTILINE
		)
		while move_match:
			moves.extend([move_match.group(1), move_match.group(2)])
			moves_string = move_match.group(3)
			move_match = re.match(
				"[0-9]*?\.(.*?) (.*?) (.*)",
				moves_string,
				flags=re.DOTALL | re.MULTILINE
			)
		# We need to do one last match with a slightly different re to handle the
		# case where White won (We need to add only Whites move).
		move_match = re.match(
			"[0-9]*?\.(.*?) 1-0.*",
			moves_string,
			flags=re.DOTALL | re.MULTILINE
		)
		if move_match:
			moves.append(move_match.group(1))

		return moves


class TimeControlTransformer(etl.SingleElementTransformer):

	transform_arguments = set(['time_control_string'])
	return_names = set(['time_control'])

	def _transform(self, time_control_string=''):
		match = re.search('(.*)\|(.*)', time_control_string)

		if match:
			return (int(match.group(1)), int(match.group(2)))
		raise DataError()


class ChessDotComUserTransformer(etl.SingleElementTransformer):

	transform_arguments = set(['username'])
	return_names = set(['user_id'])

	def _transform(self, username=None):
		return models.ChessDotComUser.find_user_by_username(
			username,
			create_if_not_found=True
		)


class ChessDotComGameLoader(etl.ModelLoader):

	extractors = {
		'moves': MovesExtractor(),
		'white_username': MetaDataExtractor('White'),
		'black_username': MetaDataExtractor('Black'),
		'white_elo': MetaDataExtractor('WhiteElo'),
		'black_elo': MetaDataExtractor('BlackElo'),
		'date_played': MetaDataExtractor('Date'),
		'time_control': MetaDataExtractor('TimeControl')
	}

	transformers = [
		MovesTransformer(element_name='moves'),
		TimeControlTransformer(element_name='time_control'),
		etl.DateTransformer(element_name='date_played'),
		etl.IntegerTransformer(element_name='white_elo'),
		etl.IntegerTransformer(element_name='black_elo'),
		ChessDotComUserTransformer(
			input_name='white_username',
			output_name='white_user'
		),
		ChessDotComUserTransformer(
			input_name='black_username',
			output_name='black_user'
		)
	]

	model_class = models.ChessDotComGame

	def execute(self, raw_data):
		"""Accepts a (game_id, pgn) tuple."""
		self.chess_dot_com_id = raw_data[0]
		try:
			game = models.ChessDotComGame.objects.get(
				chess_dot_com_id=self.chess_dot_com_id
			)
		except models.ChessDotComGame.DoesNotExist:
			# The game doesn't exist so we need to load it.
			return super(ChessDotComGameLoader, self).execute(raw_data[1])
		else:
			# The game already exists; just return it.
			return game
