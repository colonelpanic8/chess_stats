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
}).factory('HistoryRequestor', function() {

  function HistoryRequestor(username, port) {
    this.username = username;
    this.webSocket = new WebSocket(
      "ws://{0}:{1}/fetch_games/".format(document.domain, port)
    );
    this.messageHandlers = [];
    this.webSocket.onmessage = this.handleMessage.bind(this);
  }
  
  HistoryRequestor.prototype = {
    requestRefreshGames: function() {
      var json_string = JSON.stringify({
        "type": "GET_GAMES",
        "username": this.username
      })
      this.webSocket.send(json_string)
    },
    addMessageHandler: function(handler) {
      this.messageHandlers.push(handler);
    },
    handleMessage: function(messageEvent) {
      var message = JSON.parse(messageEvent.data);
      _.each(this.messageHandlers, function(handler) {
        handler(message);
      });
    }
  }
  return HistoryRequestor;
});
