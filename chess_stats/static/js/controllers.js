String.prototype.format = function() {
  var formatted = this;
  for (var i = 0; i < arguments.length; i++) {
    var regexp = new RegExp('\\{'+i+'\\}', 'gi');
    formatted = formatted.replace(regexp, arguments[i]);
  }
  return formatted;
};

function NavigationCtrl($scope, State) {
  $scope.state = State;
}

function LoginCtrl($scope, $location) {
  $scope.login = function(username) {
    $location.path("/" + $scope.username + "/rating_graph");
  }
};

function RatingGraphCtrl($scope, $location, $routeParams, State) {
  $scope.username = $routeParams.username;
  State.username = $scope.username;
  console.log($scope.username);
}

function GameHistoryCtrl($scope, HistoryRequestor, $route, $routeParams, State, $location) {
  $scope.username = $routeParams.username
  State.username = $scope.username;
  console.log($scope.username);
  $scope.goToAnalysisView = function (chessDotComID) {
    $location.path("/interactive_analysis/{0}".format(chessDotComID))
  }
  $scope.gameHistory = [];
  $scope.addGameToGameHistory = function(newGame) {
    $scope.gameHistory.splice(_.sortedIndex($scope.gameHistory, newGame, function(game) {
      return -game.id;
    }), 0, newGame);
    $scope.$apply()
  }
  $scope.goToUsername = function(username) {
    $location.path("/" + username + "/game_history")
  }
  $scope.historyRequestor = new HistoryRequestor($scope.username, location.port || "80");
  $scope.historyRequestor.addGameHandler($scope.addGameToGameHistory);
  $scope.historyRequestor.requestRefreshGames();
}

function InteractiveAnalysisCtrl($scope, AnalysisClient, requestGame, $route, $routeParams) {
  $scope.chessGame = new ChessGame();

  $scope.game = null;
  if($routeParams) {
    $scope.game = requestGame($routeParams.chessDotComID);
    debugger;
    _.each($scope.game.moves, function(algebraicMove) {
      $scope.chessGame.makeMoveFromAlgebraic(algebraicMove);
    });
  }
  
  $scope.requestAnalysis = function() {
    $scope.analysisClient.setPosition(_.map(this.chessGame.movesList, function(move) {
      return move.uci
    }));
    $scope.analysisClient.startAnalysis();
  }
  $scope.bestMove = 'N/A';
  $scope.continuation = 'N/A';
  $scope.score = 0;
  $scope.handleAnalysis = function(analysisMessage) {
    $scope.chessGame.makeMoveFromUCI(analysisMessage.analysis.best_move);
    $scope.score = analysisMessage.analysis.centipawn_score / 100;
    $scope.bestMove = analysisMessage.analysis.best_move;
    $scope.continuation = analysisMessage.analysis.continuation_string.split(" ").slice(0, 3).join(" ");
    $scope.$apply();
  }

  $scope.analysisClient = new AnalysisClient(location.port || "80");
  $scope.analysisClient.addMessageHandler($scope.handleAnalysis);
}

function MoveAnalysisCtrl($scope, $http, StatsFetcher, ChessGame, $routeParams, State) {
  $scope.username = $routeParams.username;
  State.username = $scope.username;
  $scope.chessGame = new ChessGame();
  $scope.movesStatsList = [];
  $scope.refreshMoveStatsList = function() {
    $scope.statsFetcher.fetchStatsForMoves($scope.chessGame.movesList);
  }
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

