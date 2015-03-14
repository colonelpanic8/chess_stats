from flask.ext.sqlalchemy import SQLAlchemy
import simplejson
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import composite
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

    def __repr__(self):
        return '<ChessDotComUser(\'{0}\')'.format(self.username)


class TimeControl(object):

    def __init__(self, starting_time, move_time_bonus, *args):
        self.starting_time = starting_time
        self.move_time_bonus = move_time_bonus

    @property
    def estimated_game_minutes(self):
        return self.starting_time + (float(40 * self.move_time_bonus)/60)

    def __composite_values__(self):
        return self.starting_time, self.move_time_bonus, self.time_control_type

    @property
    def time_control_type(self):
        if self.estimated_game_minutes <= 3:
            return 'bullet'
        elif self.estimated_game_minutes < 15:
            return 'blitz'
        else:
            return 'standard'


class PositionAnalysis(db.Model):

    moves = db.Column(db.String, unique=True, index=True, primary_key=True)
    centipawn_score = db.Column(db.Integer)
    best_move_uci = db.Column(db.String)

    @property
    def uci_moves_list(self):
        return parse_long_uci_string(self.moves)

    @classmethod
    def uci_moves_string_filter(cls, uci_moves_string):
        return cls.moves == uci_moves_string

    @classmethod
    def uci_moves_list_filter(cls, uci_moves_list):
        return cls.uci_moves_string_filter(''.join(uci_moves_list))


class ChessDotComGame(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    chess_dot_com_id = db.Column(db.Integer, unique=True)
    date_played = db.Column(db.Date())

    white_elo = db.Column(db.Integer)
    white_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

    black_elo = db.Column(db.Integer)
    black_user_id = db.Column(db.Integer, db.ForeignKey(ChessDotComUser.id))

    moves = db.Column(db.String, index=True)
    result = db.Column(
        db.Enum(
            common.WHITE_VICTORY,
            common.BLACK_VICTORY,
            common.DRAW,
            name='Result'
        )
    )
    termination = db.Column(
        db.Enum(
            common.CHECKMATE,
            common.TIME,
            common.RESIGNATION,
            common.AGREEMENT,
            common.INSUFFICIENT_MATERIAL,
            common.STALEMATE,
            common.ABANDONED,
            common.REPETITION,
            common.FIFTY_MOVE
        ),
        name='Termination'
    )

    starting_time = db.Column(db.Integer)
    move_time_bonus = db.Column(db.Integer)
    time_control_type = db.Column(db.Enum('blitz', 'bullet', 'standard'))

    time_control = composite(TimeControl, starting_time,
                             move_time_bonus, time_control_type)

    @classmethod
    def username_games_filter(cls, username):
        cls.ChessDotComUser.username == username

    @classmethod
    def uci_moves_list_filter(cls, uci_moves_list):
        return cls.uci_moves_string_filter(''.join(uci_moves_list))

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

    def __repr__(self):
        return '<ChessDotComGame(\'{0}\' v \'{1}\')>'.format(
            self.white_username,
            self.black_username
        )
