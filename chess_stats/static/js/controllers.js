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
}

function GameHistoryCtrl($scope, HistoryRequestor, $route, $routeParams, State, $location, goToUsername) {
  $scope.username = $routeParams.username
  State.username = $scope.username;
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
  $scope.goToUsername = goToUsername;
  $scope.historyRequestor = new HistoryRequestor($scope.username, location.port || "80");
  $scope.historyRequestor.addGameHandler(function(data) {
    if(data instanceof Array) {
      $scope.gameHistory.push.apply($scope.gameHistory, data);
      $scope.gameHistory.sort(function(left, right) {
        return left.chess_dot_com_id < right.chess_dot_com_id;
      });
      $scope.$apply();
      return;
    }
    $scope.addGameToGameHistory(data);
  });
  $scope.historyRequestor.requestRefreshGames();
}

function InteractiveAnalysisCtrl($scope, AnalysisClient, requestGame, $route, $routeParams, goToUsername) {
  $scope.goToUsername = goToUsername;
  $scope.chessGame = new ChessGame();

  $scope.game = null;
  if($routeParams.chessDotComID) {
    $scope.game = requestGame($routeParams.chessDotComID);
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
    var move = $scope.chessGame.notationProcessor.parseUCIMove(analysisMessage.analysis.best_move);
    $scope.squareSet.setNewHighlight(move.sourceIndex, "red");
    $scope.squareSet.setHighlight(move.destIndex, "blue");
    $scope.score = analysisMessage.analysis.centipawn_score / 100;
    $scope.bestMove = analysisMessage.analysis.best_move;
    $scope.continuation = analysisMessage.analysis.continuation_string.split(" ").slice(0, 3).join(" ");

    $scope.chessGame.addListener(function() {
      $scope.squareSet.clearHighlights();
    });
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
      return !(algebraicMoves.indexOf(move.uci) < 0);
  });
}

