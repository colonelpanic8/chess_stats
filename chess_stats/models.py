from flask.ext.sqlalchemy import SQLAlchemy
import simplejson
from sqlalchemy.types import INTEGER, TypeDecorator, VARCHAR
from sqlalchemy.orm.exc import NoResultFound
from chess_game import ChessGame, parse_long_uci_string

from . import app
from . import common


db = SQLAlchemy(app)
db.Model.itercolumns = classmethod(lambda cls: cls.__table__.columns._data.iterkeys())


class UCIBackedMovesType(TypeDecorator):

    # Type that exposes Move objects instead of the underlying uci move string
    # Was far too slow in practice

    impl = VARCHAR

    def process_result_value(self, uci_moves_string, dialect):
        if isinstance(uci_moves_string, basestring):
            playable_game = ChessGame()
            return playable_game.make_moves_from_long_uci_string(uci_moves_string)
        return uci_moves_string

    def process_bind_param(self, moves, dialect):
        if isinstance(moves, basestring):
            return moves
        if isinstance(moves[0], basestring):
            return ''.join(moves)
        return ''.join(move.uci for move in moves)


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


class AnalysisScore(object):

    def __init__(self, value, is_mate_in_n=False):
        self.value = value
        self.is_mate_in_n = is_mate_in_n


class AnalysisScoreType(TypeDecorator):

    impl = INTEGER

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.score * 2
            if value.is_mate_in_n:
                value += 1
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = AnalysisScore(value / 2, bool(value & 1))
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

    chess_dot_com_id = db.Column(db.Integer, unique=True)
    date_played = db.Column(db.Date())

    white_elo = db.Column(db.Integer)
    white_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

    black_elo = db.Column(db.Integer)
    black_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

    moves = db.Column(db.String)
    result = db.Column(
        db.Enum(
            common.WHITE_VICTORY,
            common.BLACK_VICTORY,
            common.DRAW,
            name='Result'
        )
    )

    @classmethod
    def username_games_filter(cls, username):
        cls.ChessDotComUser.username == username

    @classmethod
    def uci_moves_string_filter(cls, uci_moves_string):
        return cls.moves.like('{0}%'.format(uci_moves_string))

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
    def moves_list(self):
        return ChessGame().make_moves_from_long_uci_string(self.moves)

    @property
    def uci_moves_list(self):
        return parse_long_uci_string(self.moves)

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
            'moves': self.uci_moves_list,
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