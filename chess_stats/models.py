from django.db import models
from . import fields

class ChessComUser(models.Model):

	user_name = models.CharField(max_length=20)
	date_joined = models.DateField(auto_now=True)


class ChessDotComGame(models.Model):

	date_played = models.DateField()

	white_rating = models.PositiveIntegerField()
	black_rating = models.PositiveIntegerField()

	white_user = models.ForeignKey(ChessComUser)
	black_user = models.ForeignKey(ChessComUser)

	moves = fields.JSONField()
