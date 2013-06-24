String.prototype.format = function() {
  var formatted = this;
  for (var i = 0; i < arguments.length; i++) {
    var regexp = new RegExp('\\{'+i+'\\}', 'gi');
    formatted = formatted.replace(regexp, arguments[i]);
  }
  return formatted;
};

function NavigationCtrl($scope) {
  
}

function LoginCtrl($scope, $location) {
  $scope.loginUsername = function() {
    window.location = "rating_graph/" + $scope.username;
  }
};

function GameBrowseCtrl($scope, HistoryRequestor) {
  $scope.init = function(username, port) {
    $scope.username = username;
    $scope.port = port;
    $scope.historyRequestor = new HistoryRequestor($scope.username, $scope.port);
    $scope.historyRequestor.addGameHandler($scope.addGameToGameHistory);
    $scope.historyRequestor.requestRefreshGames();
  }
  $scope.buildChessDotComGameURL = function (id) {
    return "http://www.chess.com/livechess/game?id={0}".format(id)
  }
  $scope.gameHistory = [];
  $scope.addGameToGameHistory = function(newGame) {
    $scope.gameHistory.splice(_.sortedIndex($scope.gameHistory, newGame, function(game) {
      return -game.id;
    }), 0, newGame);
    $scope.$apply()
  }
}

function MoveStatsCtrl($scope, $http, StatsFetcher, ChessGame) {
  $scope.chessGame = new ChessGame();
  $scope.movesStatsList = [];
  $scope.refreshMoveStatsList = function() {
    $scope.statsFetcher.fetchStatsForMoves($scope.chessGame.movesList);
  }
  $scope.init = function(username) {
    $scope.username = username;
    $scope.statsFetcher = new StatsFetcher(
      $scope.username,
      'white',
      function(moveStatsList) {
        $scope.moveStatsList = moveStatsList;
      }
    );
    $scope.refreshMoveStatsList();
    $scope.chessGame.addListener($scope.refreshMoveStatsList);
    $scope.chessGame.addMoveChecker(function(move, isUndo) {
      if(isUndo) return true;
      var algebraicMoves = _.map($scope.moveStatsList, function(moveStats) {
        return moveStats.move
      });
      return !(algebraicMoves.indexOf(move.algebraic) < 0);
    });
  }
}
