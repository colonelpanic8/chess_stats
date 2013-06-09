import datetime

import testify as T

from chess_stats import models
from chess_stats.user_rating_history_fetcher import UserRatingHistoryFetcher
from . import ChessStatsSandboxedTestCase


class UserRatingHistoryFetcherTestCase(ChessStatsSandboxedTestCase):

    @T.setup_teardown
    def build_users(self):
        self.white_user = models.ChessDotComUser(username="white")
        self.black_user = models.ChessDotComUser(username="black")
        self.date_game_played = datetime.date(year=2013, day=1, month=1)
        self.game = models.ChessDotComGame(
            chess_dot_com_id=22,
            date_played=self.date_game_played,
            white_user=self.white_user,
            black_user=self.black_user,
            white_elo=1234,
            black_elo=1311
        )
        models.db.session.add(self.white_user)
        models.db.session.add(self.black_user)
        models.db.session.add(self.game)
        models.db.session.commit()
        yield

    def test_black_user_rating_history_fetch(self):
        fetcher = UserRatingHistoryFetcher(self.black_user.username)
        rating_history = fetcher.get_user_rating_history()

        T.assert_isinstance(rating_history, list)
        T.assert_equal(
            rating_history,
            [
                {
                    "elo": self.game.black_elo,
                    "date_played": {
                        "day": self.game.date_played.day,
                        "month": self.game.date_played.month,
                        "year": self.game.date_played.year
                    },
                    "chess_dot_com_id": self.game.chess_dot_com_id
                }
            ]
        )

    def test_white_user_rating_history_fetch(self):
        fetcher = UserRatingHistoryFetcher(self.white_user.username)
        rating_history = fetcher.get_user_rating_history()

        T.assert_isinstance(rating_history, list)
        T.assert_equal(
            rating_history,
            [
                {
                    "elo": self.game.white_elo,
                    "date_played": {
                        "day": self.game.date_played.day,
                        "month": self.game.date_played.month,
                        "year": self.game.date_played.year
                    },
                    "chess_dot_com_id": self.game.chess_dot_com_id
                }
            ]
        )

if __name__ == '__main__':
    testify.run()