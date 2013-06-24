angular.module('ChessStats.factories', []).factory('StatsFetcher', function($http) {
  function StatsFetcher(username, color, successCallback) {
    this.username = username;
    this.color = color;
    this.successCallback = successCallback;
  }

  StatsFetcher.prototype.fetchStatsForMoves = function(moves) {
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
  return StatsFetcher;
}).factory('HistoryRequestor', function($http) {

  function HistoryRequestor(username, port) {
    this.username = username;
    this.gameHandlers = [];
    this.webSocket = null;
    this.port = port;
  }
  
  HistoryRequestor.prototype = {
    requestRefreshGames: function() {
      this.webSocket = new WebSocket(
        "ws://{0}:{1}/fetch_games/".format(document.domain, this.port)
      );
      var boundHandleMessage = this.handleGame.bind(this);
      this.webSocket.onmessage = function(messageEvent) {
        var message = JSON.parse(messageEvent.data)
        if(message.type == "START") {
          this.webSocket.send(JSON.stringify({
            "type": "GET_GAMES",
            "username": this.username
          }));
        } else {
          boundHandleGame(message.game);
        }
      }.bind(this);
    },
    requestExistingGames: function() {
      $http({
        'method': 'GET',
        'url': '/get_game_history/' + this.username,
      }).success(function(gameHistory) {
        _.each(gameHistory, function(game) {
          this.handleGame(game)
        }, this);
      }.bind(this));
    },
    addGameHandler: function(handler) {
      this.gameHandlers.push(handler);
    },
    handleGame: function(game) {
      _.each(this.gameHandlers, function(handler) {
        handler(game);
      });
    },
      
  }
  return HistoryRequestor;
});
