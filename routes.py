from app import app


@app.route("/chess_stats/browse_games")
def browse_games():
	return "Test"

if __name__ == "__main__":
    app.run()
