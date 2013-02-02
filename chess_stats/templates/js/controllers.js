'use strict';

/* Controllers */

function AppCtrl($scope, $http) {
	$scope.moves_list = [];
	$scope.username = 'AlexMalison'
	$scope.getMoves = function() {
		var moves_json = JSON.stringify($scope.moves_list)
		var moves_string = encodeURIComponent(moves_json)
		$http.get(
			'/chess_stats/get_stats?moves='+moves_string+'&username='+$scope.username
		).success(
				function(data) {
					$scope.moves = data;
				});
	}
	$scope.alterMoves = function($move) {
		$scope.moves_list.push($move)
		$scope.getMoves()
	}
	$scope.back = function() {
		$scope.moves_list.pop()
		$scope.getMoves()
	}
	$scope.setUsername = function(username) {
		$scope.username = username
		$scope.moves_list = []
		$scope.getMoves()
	}
	$scope.getMoves([]);
}
