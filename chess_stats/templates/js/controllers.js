'use strict';

function MoveStatsCtrl($scope, $http) { 
	console.log('test')
	$scope.moves = [];
	$scope.moveStatsPairs = [];
	$scope.username = 'AlexMalison';

	$scope.getMoves = function() {
		$http.get(
			{
				url: '/chess_stats/get_stats',
				params: {
					moves: JSON.stringify($scope.moves_list)
					username: $scope.username
				}
			}
		).success(
			function(moveStatsPairs) {
				$scope.moveStatsPairs = moveStatsPairs;
			}
		);
	}

	$scope.addMove = function(move) {
		$scope.moves.push(move);
		$scope.getMoves();
	}

	$scope.removeLastNMoves(numMovesToRemove) = function() {
		$scope.moves_list.slice(0, -1*numMovesToRemove);
		$scope.getMoves();
	}

	$scope.setUsername = function(username) {
		$scope.username = username;
		$scope.moves_list = [];
		$scope.getMoves();
	}

	$scope.getMoves();
}
