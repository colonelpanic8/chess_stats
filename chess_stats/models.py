from django.db import models
from . import fields


class ChessDotComUser(models.Model):

	username = models.CharField(max_length=20, unique=True)
	date_joined = models.DateField(auto_now=True)

	@classmethod
	def find_user_by_username(cls, username, create_if_not_found=False):
		try:
			cls.objects.get(username=username)
		except cls.DoesNotExist:
			if create_if_not_found:
				user = cls(username=username)
				user.save()
				return user


class ChessDotComGame(models.Model):

	date_played = models.DateField()

	white_elo = models.PositiveIntegerField()
	black_elo = models.PositiveIntegerField()

	white_user = models.ForeignKey(ChessDotComUser, related_name='white_games')
	black_user = models.ForeignKey(ChessDotComUser, related_name='black_games')

	moves = fields.JSONField()
