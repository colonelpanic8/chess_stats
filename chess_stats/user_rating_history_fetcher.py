from . import models


class UserRatingHistoryFetcher(object):

    def __init__(self, username):
        self.username = username
        self.user = models.ChessDotComUser.find_user_by_username(self.username)

    def get_user_rating_history(self):
        user_games = self.user.all_games.order_by('chess_dot_com_game_id').all()
        return [self.build_user_game_data_from_game(game) for game in user_games]

    def build_user_game_data_from_game(self, game):
        opponent = game.white_user if game.black_user == self.user else game.black_user
        return {
            "elo": game.white_elo if game.white_user == self.user else game.black_elo,
            "opponent": opponent.username,
            "opponent_elo": game.black_elo if game.white_user == self.user else game.white_elo,
            "date_played": {
                "day": game.date_played.day,
                "month": game.date_played.month,
                "year": game.date_played.year
            },
            "chess_dot_com_id": game.chess_dot_com_id
        }