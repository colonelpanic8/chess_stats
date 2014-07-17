from contextlib import closing
from datetime import datetime
from urllib import urlopen
import re

from chess_game import ChessGame

from . import common
from . import etl
from . import models


class DataError(Exception):
    pass


class ChessDotComGameExtractor(etl.Extractor):

    BASE_URL = "http://www.chess.com/"
    PGN_LINK_FORMAT = '{base_url}{game_type}/download_pgn.html?lid={game_id}'

    def extract(self, chess_dot_com_game_id):
        """Download the pgn associated with game_id from chess.com"""

        # It seems that chess.com always uses echess here, even for live games.
        url = self.PGN_LINK_FORMAT.format(
            base_url=self.BASE_URL,
            game_type='echess',
            game_id=chess_dot_com_game_id
        )
        with closing(urlopen(url)) as pgn_file:
            return pgn_file.read()


class MovesTransformer(etl.Transformer):

    transform_arguments = set(['moves_string'])

    moves_matcher = re.compile(
        "[0-9]*?\.(.*?) (.*?) (.*)",
        flags=re.DOTALL|re.MULTILINE
    )

    def get_moves_string(self, pgn_string):
        moves_match = re.search(
            "^(1\..*)",
            pgn_string,
            flags=re.DOTALL | re.MULTILINE
        )
        if not moves_match:
            return ''
        return moves_match.group(1)

    def transform(self, pgn_string):
        moves_string = self.get_moves_string(pgn_string)
        moves_string = moves_string.replace('\r\n', '')

        moves = []
        move_match = self.moves_matcher.match(moves_string)
        while move_match:
            moves.extend([move_match.group(1), move_match.group(2)])
            moves_string = move_match.group(3)
            move_match = self.moves_matcher.match(moves_string)

        # We need to do one last match with a slightly different RE to handle the
        # case where White won while it was black's turn. This happens when white
        # wins by checkmate or when black resigns during his own turn.
        move_match = re.match(
            "[0-9]*?\.(.*?) 1-0.*",
            moves_string,
            flags=re.DOTALL | re.MULTILINE
        )
        if move_match:
            moves.append(move_match.group(1))

        return moves


class UCITransformer(etl.Transformer):

    def transform(self, algebraic_moves):
        game = ChessGame()
        return ''.join(game.make_move_from_algebraic_and_return_uci(move)
                       for move in algebraic_moves)


class MetaDataTransformer(etl.Transformer):

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

    def transform(self, pgn_string):
        return self._transform(self.extract(pgn_string))

    def _transform(self, attribute_string):
        raise NotImplemented()


class DateTransformer(MetaDataTransformer):

    DATE_FORMAT = '%Y.%m.%d'

    def _transform(self, date_string):
        return datetime.strptime(date_string, self.DATE_FORMAT).date()


class IntegerTransformer(MetaDataTransformer):

    def _transform(self, string=None):
        return int(string)


class TimeControlTransformer(MetaDataTransformer):

    transform_arguments = set(['time_control_string'])

    def _transform(self, time_control_string):
        match = re.search('(.*)\|(.*)', time_control_string)

        if match:
            return models.TimeControl(int(match.group(1)), int(match.group(2)))
            raise DataError()


class ChessDotComUserTransformer(MetaDataTransformer):

    def _transform(self, username):
        return models.ChessDotComUser.find_user_by_username(
            username,
            create_if_not_found=True
        ).id


class ResultTransformer(MetaDataTransformer):

    result_matcher = re.compile('(.*?)-.*?')

    def _transform(self, result_string):
        white_points = self.result_matcher.match(result_string).group(1)
        if white_points == '1':
            return common.WHITE_VICTORY
        elif white_points == '0':
            return common.BLACK_VICTORY
        else:
            return common.DRAW


class ChessDotComGameLoader(object):

    @classmethod
    def load(cls, transformed):
        game = models.ChessDotComGame.query.filter(
            models.ChessDotComGame.chess_dot_com_id == transformed['chess_dot_com_id']
        ).first()
        if not game:
            game = models.ChessDotComGame(**transformed)
        else:
            for key, value in transformed.items():
                setattr(game, key, value)
        return game


class ChessDotComGameETL(etl.ETL):

    extractor = ChessDotComGameExtractor()

    transformers = {
        'moves': etl.ComposeTransformer(MovesTransformer(), UCITransformer()),
        'white_user_id': ChessDotComUserTransformer('White'),
        'black_user_id': ChessDotComUserTransformer('Black'),
        'white_elo': IntegerTransformer('WhiteElo'),
        'black_elo': IntegerTransformer('BlackElo'),
        'date_played': DateTransformer('Date'),
        'time_control': TimeControlTransformer('TimeControl'),
        'result': ResultTransformer('Result')
    }

    loader = ChessDotComGameLoader

    def __init__(self, identifier):
        super(ChessDotComGameETL, self).__init__(identifier)
        self.transformed['chess_dot_com_id'] = identifier

    def execute(self, force_refresh=False):
        if force_refresh:
            return super(ChessDotComGameETL, self).execute()
        try:
            game = models.ChessDotComGame.query.filter(
                models.ChessDotComGame.chess_dot_com_id ==
                self.transformed['chess_dot_com_id']
            ).one()
        except models.NoResultFound:
            # The game doesn't exist so we need to load it.
            return super(ChessDotComGameETL, self).execute()
        # The game already exists; just return it.
        return game


class ChessDotComGameFileExtractor(object):

    def extract(self, filename):
        with open(filename, 'r') as file:
            return file.read()


class ChessDotComGameFileETL(ChessDotComGameETL):

    id_matcher = re.compile('.*? - (.*?)\.pgn')

    extractor = ChessDotComGameFileExtractor()

    def __init__(self, filepath):
        etl.ETL.__init__(self, filepath)
        matches = self.id_matcher.search(filepath)
        if not matches:
            import ipdb; ipdb.set_trace()
        else:
            print filepath

        self.transformed['chess_dot_com_id'] = matches.group(1)
