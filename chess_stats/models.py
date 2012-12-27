from django.db import models
from . import fields


class ChessDotComUser(models.Model):

	username = models.CharField(max_length=20, unique=True)
	date_joined = models.DateField(auto_now=True)

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


class ChessDotComGame(models.Model):

	chess_dot_com_id = models.PositiveIntegerField(unique=True)
	date_played = models.DateField()

	white_elo = models.PositiveIntegerField()
	white_user = models.ForeignKey(ChessDotComUser, related_name='white_games')

	black_elo = models.PositiveIntegerField()
	black_user = models.ForeignKey(ChessDotComUser, related_name='black_games')

	moves = fields.JSONField()

	@property
	def black_username(self):
		return self.black_user.username

	@property
	def white_username(self):
		return self.white_user.username

