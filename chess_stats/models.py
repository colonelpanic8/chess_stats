import simplejson

from django.db import models

from . import fields


class ChessDotComUser(models.Model):

	username = models.CharField(max_length=20, unique=True)
	date_joined = models.DateField(auto_now=True)

	last_scanned_chess_dot_com_game_id = models.PositiveIntegerField(null=True)

	def __unicode__(self):
		return self.username

	@classmethod
	def find_user_by_username(cls, username, create_if_not_found=False):
		try:
			return cls.objects.get(username=username)
		except cls.DoesNotExist:
			if create_if_not_found:
				user = cls(username=username)
				user.save()
				return user
			raise

	@classmethod
	def load_games_by_username(cls, username):
		"""Return games stored associated with `username`."""
		user = cls.objects.get(username=username)
		return user.white_games.all() + user.black_games.all()

	@property
	def all_games(self):
		"""Return all games associated with the user sorted by date with more
		recently played games coming first.
		"""
		return ChessDotComGame.objects.filter(
			models.Q(black_user=self) | models.Q(white_user=self)
		).order_by('-date_played', '-chess_dot_com_id')

	@property
	def most_recently_played_game_in_records(self):
		try:
			return self.all_games[0]
		except IndexError:
			return None


class ChessDotComGame(models.Model):

	chess_dot_com_id = models.PositiveIntegerField(null=True)
	date_played = models.DateField()

	white_elo = models.PositiveIntegerField()
	white_user = models.ForeignKey(ChessDotComUser, related_name='white_games')

	black_elo = models.PositiveIntegerField()
	black_user = models.ForeignKey(ChessDotComUser, related_name='black_games')

	moves = fields.JSONField()
	victor_was_white = models.NullBooleanField(null=True)

	@property
	def black_username(self):
		return self.black_user.username

	@property
	def white_username(self):
		return self.white_user.username

	@property
	def as_dict(self):
		return {
			'id': self.chess_dot_com_id,
			'date_played': str(self.date_played),
			'white_username': self.white_username,
			'black_username': self.black_username,
			'white_elo': self.white_elo,
			'black_elo': self.black_elo,
			'moves': self.moves,
			'victor_was_white': self.victor_was_white
		}

	@property
	def as_json(self):
		return simplejson.dumps(self.as_dict)


	def __unicode__(self):
		return ' '.join(
			[
				self.white_username,
				'vs.',
				self.black_username,
				'-',
				str(self.date_played),
				str(self.chess_dot_com_id),
			]
		)

	def matches_moves(self, moves):
		for game_move, match_move in zip(self.moves, moves):
			if game_move != match_move:
				return False
		return True
