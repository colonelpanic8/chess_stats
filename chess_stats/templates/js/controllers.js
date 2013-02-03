'use strict';

function MoveStatsCtrl($scope, $http) { 
	$scope.moves = [];
	$scope.moveStatsList = [];
	$scope.username = 'AlexMalison';

	$scope.getMoves = function() {
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
	}

	$scope.addMove = function(move) {
		$scope.moves.push(move);
		$scope.getMoves();
	}

	$scope.setUsername = function(username) {
		$scope.username = username;
		$scope.moves = [];
		$scope.getMoves();
	}

	$scope.removeLastNMoves = function(numMovesToRemove) {
		console.log(numMovesToRemove)
		$scope.moves = $scope.moves.slice(0, numMovesToRemove*-1);
		$scope.getMoves();
	}

	$scope.colorElement = function($element) {
		console.log($element)
	}


	$scope.getMoves()
}
