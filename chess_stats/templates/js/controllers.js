'use strict';

function MoveStatsCtrl($scope, $http) { 
	$scope.moves = [];
	$scope.moveStatsPairs = [];
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
				$scope.moveStatsPairs = newValue;
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

	$scope.getMoves()
}
