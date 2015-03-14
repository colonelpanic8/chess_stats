from . import models
from . import chess_dot_com_etl


def segment(iterable, segment_length):
    if segment_length is None:
        yield iterable
        raise StopIteration
    def yield_length():
        for _ in xrange(segment_length):
            yield iterable.next()
    while True:
        segment = list(yield_length())
        if not segment:
            raise StopIteration
        yield segment


class Refresher(object):

    @classmethod
    def refresh(self, games=None):
        games = games or iter(models.ChessDotComGame.query)
        for game_list in segment(games, 30):
            for game in game_list:
                game = chess_dot_com_etl.ChessDotComGameETL(game.chess_dot_com_id).execute(True)
                models.db.session.add(game)
                print game
            models.db.session.commit()
