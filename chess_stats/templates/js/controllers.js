'use strict';

function MoveStatsCtrl($scope, $http) { 
	$scope.moves = [];
	$scope.movePairs = []
	$scope.moveStatsList = [];
	$scope.username = 'AlexMalison';

	$scope.refreshMoveStatsList = function() {
		$http(
			{
				'method': 'GET',
				'url': '/chess_stats/get_stats',
				'params': {
					'moves': $scope.moves,
					'username': $scope.username
				}
			}
		).success(
			function(newValue) {
				$scope.moveStatsList = newValue;
			}
		);
		$scope.movePairs = $scope.getMovePairs()
	}

	$scope.addMove = function(move) {
		$scope.moves.push(move);
		$scope.refreshMoveStatsList();
	}

	$scope.setUsername = function(username) {
		$scope.username = username;
		$scope.moves = [];
		$scope.refreshMoveStatsList();
	}

	$scope.removeLastNMoves = function(numMovesToRemove) {
		$scope.moves = $scope.moves.slice(0, numMovesToRemove*-1);
		$scope.refreshMoveStatsList();
	}

	$scope.truncateMovesTo = function(lastIndex) {
		if(lastIndex >= $scope.moves.length) return
		$scope.moves = $scope.moves.slice(0, lastIndex+1);
		$scope.refreshMoveStatsList();
	}

	$scope.colorElement = function($element) {
		console.log($element)
	}

	$scope.getMovePairs = function() {
		var movePairs = []
		for(var i = 0; i < $scope.moves.length - 1; i += 2) {
			movePairs.push(
				{
					'index': i,
					'whiteMove': $scope.moves[i],
					'blackMove': $scope.moves[i+1],
				}
			);
		}
		if($scope.moves.length % 2 == 1) {
			
			movePairs.push(
				{
					'index': $scope.moves.length - 1,
					'whiteMove': $scope.moves[$scope.moves.length - 1],
					'blackMove': "..."
				}
			);
		}
		return movePairs
	}

	$scope.refreshMoveStatsList()
}
