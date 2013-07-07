from flask import render_template, request
import simplejson

from . import app
from . import logic
from . import models
from .user_rating_history_fetcher import UserRatingHistoryFetcher


@app.route("/browse_games/<username>")
def browse_games(username):
   return render_template('browse_games.html', username=username, port=app.port)

@app.route("/browse_moves/<username>")
def browse_user_moves(username):
   return render_template('browse_moves.html', username=username)

@app.route("/interactive_analysis")
def interactive_analysis():
   return render_template('interactive_analysis.html', port=app.port)

@app.route("/browse_moves")
def browse_moves():
   return render_template('browse_moves_all.html', username='')


@app.route("/game/<chess_dot_com_id>")
def get_game_by_chess_dot_com_id(chess_dot_com_id):
    # TODO: handle missing rows.
    return simplejson.dumps(
        models.ChessDotComGame.query.filter_by(chess_dot_com_id=chess_dot_com_id).one().as_dict()
    )


@app.route("/get_stats")
def get_game_stats():
   username = request.args.get('username', None)
   white = request.args.get('color', 'white').lower() == 'white'
   moves = simplejson.loads(request.args.get('moves', '[]'))
   if username:
      move_stats = logic.build_sorted_game_stats_for_moves_by_username(
         username,
         moves,
         white=white
      )
   else:
      move_stats = logic.build_sorted_game_stats_for_moves_for_all_games(moves)
   return simplejson.dumps(move_stats)

@app.route("/user_rating_history_json/<username>")
def user_rating_history_json(username):
   return simplejson.dumps(
      UserRatingHistoryFetcher(username).get_user_rating_history()
   )

@app.route("/get_game_history/<username>")
def get_game_history(username):
   return simplejson.dumps(
       [game.as_dict for game in logic.get_games_for_user(username)]
   )

@app.route("/rating_graph/<username>")
def user_rating_graph(username):
   return render_template('user_rating_histogram.html', username=username)

@app.route("/")
def username_login():
   return render_template('username_login.html')

if __name__ == "__main__":
   app.run()

