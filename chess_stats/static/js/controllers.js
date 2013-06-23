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

function GameBrowseCtrl($scope) {
    var gameLoader = {
        games: [],
        username: ""
    }

    gameLoader.buildChessDotComGameURL = function (id) {
        return "http://www.chess.com/livechess/game?id={0}".format(id)
    }

    gameLoader.requestGames = function () {
        var json_string = JSON.stringify({
           "type": "GET_GAMES",
           "username": this.username
        })
        gameLoader.webSocket.send(json_string)
    }

    gameLoader.handleMessage = function (message) {
        if(message.type == "START") {
            gameLoader.requestGames()
        }
        if(message.type == "GAME") {
            gameLoader.games.push(message.game)
            $scope.$apply()
        }
    }

    gameLoader.init = function (username, port) {
        gameLoader.username = username
        gameLoader.webSocket = new WebSocket(
            "ws://{0}:{1}/fetch_games/".format(document.domain, port)
        );
        gameLoader.webSocket.onopen = function (e) {}
        gameLoader.webSocket.onclose = function (e) {}
        gameLoader.webSocket.onmessage = function (messageEvent) {
            gameLoader.handleMessage(JSON.parse(messageEvent.data))
        }
    }

    $scope.gameLoader = gameLoader
}

function MoveStatsCtrl($scope, $http, StatsFetcher, ChessGame) {
  $scope.chessGame = new ChessGame();
  $scope.movesStatsList = [];
  $scope.refreshMoveStatsList = function() {
    $scope.statsFetcher.fetchStatsForMoves($scope.chessGame.movesList);
  }
  $scope.init = function(username) {
    $scope.username = username;
    $scope.statsFetcher = new StatsFetcher($scope.username, 'white', function(moveStatsList) {
      $scope.moveStatsList = moveStatsList;
    });
    $scope.refreshMoveStatsList();
    $scope.chessGame.addListener($scope.refreshMoveStatsList);
  }
}
