from flask.ext.sqlalchemy import SQLAlchemy
import simplejson
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm.exc import NoResultFound

from . import app
from . import common


db = SQLAlchemy(app)
db.Model.itercolumns = classmethod(lambda cls: cls.__table__.columns._data.iterkeys())


class JSONType(TypeDecorator):

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = simplejson.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = simplejson.loads(value)
        return value


class ChessDotComUser(db.Model):

	id = db.Column(db.Integer, primary_key=True)

	username = db.Column(db.String(length=20), unique=True)
	date_joined = db.Column(db.Date())

	last_scanned_chess_dot_com_game_id = db.Column(db.Integer)

	white_games = db.relationship(
		'ChessDotComGame',
		primaryjoin="ChessDotComGame.white_user_id==ChessDotComUser.id",
		backref='white_user',
		lazy='dynamic'
	)

	black_games = db.relationship(
		'ChessDotComGame',
		primaryjoin="ChessDotComGame.black_user_id==ChessDotComUser.id",
		backref='black_user',
		lazy='dynamic'
	)

	def __unicode__(self):
		return self.username

	@classmethod
	def find_user_by_username(cls, username, create_if_not_found=False):
		try:
			return cls.query.filter(cls.username == username).one()
		except NoResultFound:
			if create_if_not_found:
				user = cls(username=username)
				db.session.add(user)
				db.session.commit()
				return user
			raise

	@property
	def all_games(self):
		return self.white_games.union(self.black_games)


class ChessDotComGame(db.Model):

	id = db.Column(db.Integer, primary_key=True)

	chess_dot_com_id = db.Column(db.Integer)
	date_played = db.Column(db.Date())

	white_elo = db.Column(db.Integer)
	white_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

	black_elo = db.Column(db.Integer)
	black_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

	moves = db.Column(JSONType(1500))
	result = db.Column(
		db.Enum(
			common.WHITE_VICTORY,
			common.BLACK_VICTORY,
			common.DRAW,
			name='Result'
		)
	)

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

	@property
	def result_as_int(self):
		if self.result == common.WHITE_VICTORY:
			return 1
		if self.result == common.BLACK_VICTORY:
			return -1
		return 0

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
			'result': self.result
		}

	@property
	def as_json(self):
		return simplejson.dumps(self.as_dict)

	def matches_moves(self, moves):
		for game_move, match_move in zip(self.moves, moves):
			if game_move != match_move:
				return False
		return True
