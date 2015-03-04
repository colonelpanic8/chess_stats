from flask import render_template, request
import simplejson

from . import app
from . import logic
from . import models
from .user_rating_history_fetcher import UserRatingHistoryFetcher


@app.route("/game/<chess_dot_com_id>")
def get_game_by_chess_dot_com_id(chess_dot_com_id):
    # TODO: handle missing rows.
    return simplejson.dumps(
        models.ChessDotComGame.query.filter_by(chess_dot_com_id=chess_dot_com_id).one().as_dict
    )


@app.route("/get_stats")
def get_game_stats():
   username = request.args.get('username', None)
   white = request.args.get('color', 'white').lower() == 'white'
   uci_moves_string = request.args.get('moves', '')
   if username:
      move_stats = logic.build_sorted_game_stats_for_moves_by_username(
         username,
         uci_moves_string,
         white=white
      )
   else:
      move_stats = logic.build_sorted_game_stats_for_moves_for_all_games(
          uci_moves_string
        )
   return simplejson.dumps(move_stats)


@app.route("/user_rating_history_json/<username>")
def user_rating_history_json(username):
   return simplejson.dumps(
      UserRatingHistoryFetcher(username).get_user_rating_history()
   )


@app.route("/game_stats_by_opp_elo/<username>")
def game_stats_by_opp_elo(username):
    return simplejson.dumps(
        logic.PartitionByOpponentRating(username).partition_and_build_stats()
    )


@app.route("/get_game_history/<username>")
def get_game_history(username):
   return simplejson.dumps(
       [game.as_dict for game in logic.get_games_for_user(username)]
   )


@app.route("/")
def home(*args, **kwargs):
   return render_template('home.html')


if __name__ == "__main__":
   app.run()

