'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('ChessStats.services', []);

function StatsFetcher(username, color, successCallback) {
  this.username = username;
  this.color = color;
  this.successCallback = successCallback;
}

StatsFetcher.prototype.fetchStatsForMoves(moves) {
  $http({
    'method': 'GET',
    'url': '/get_stats',
    'params': {
      'moves': _.map(moves, function(move) { return move.algebraic }),
      'username': this.username,
      'color': this.color
    }
  }).success(this.successCallback);
}
angular.module('ChessGame.factories').factory('StatsFetcher', function() { return StatsFetcher; });
