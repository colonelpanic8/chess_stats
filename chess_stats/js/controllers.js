'use strict';

function MoveStatsCtrl($scope, $http) {
	var moveControl = {
		moves: [],
		movePairs: [],
		moveStatsList: [],
		username: 'AlexMalison'
	}

	moveControl.refreshMoveStatsList = function() {
		$http(
			{
				'method': 'GET',
				'url': '/chess_stats/get_stats',
				'params': {
					'moves': this.moves,
					'username': this.username
				}
			}
		).success(
			function(newValue) {
				moveControl.moveStatsList = newValue;
			}
		);
		this.movePairs = this.getMovePairs()
	}

	moveControl.addMove = function(move) {
		this.moves.push(move);
		this.refreshMoveStatsList();
	}

	moveControl.setUsername = function(username) {
		this.username = username;
		this.moves = [];
		this.refreshMoveStatsList();
	}

	moveControl.removeLastNMoves = function(numMovesToRemove) {
		this.moves = this.moves.slice(0, numMovesToRemove*-1);
		this.refreshMoveStatsList();
	}

	moveControl.truncateMovesTo = function(lastIndex) {
		if(lastIndex >= this.moves.length) return
		this.moves = this.moves.slice(0, lastIndex);
		this.refreshMoveStatsList();
	}

	moveControl.getMovePairs = function() {
		var movePairs = []
		for(var i = 0; i < this.moves.length - 1; i += 2) {
			movePairs.push(
				{
					'index': i,
					'whiteMove': this.moves[i],
					'blackMove': this.moves[i+1],
				}
			);
		}
		if(this.moves.length & 0x1 == 1) {			
			movePairs.push(
				{
					'index': this.moves.length - 1,
					'whiteMove': this.moves[this.moves.length - 1],
					'blackMove': "..."
				}
			);
		} else {
			movePairs.push(
				{
					'index': this.moves.length,
					'whiteMove': "...",
					'blackMove': ""
				}
			);
		};
		return movePairs
	}

	moveControl.refreshMoveStatsList()
	$scope.moveControl = moveControl
}
