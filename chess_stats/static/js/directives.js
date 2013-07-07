'use strict';

/* Directives */
var directives = angular.module('ChessStats.directives', [])

directives.directive(
  'jqAnimate',
  function(jQueryExpression, templateElement){ 
    return function(instanceElement){
      instanceElement.show('slow'); 
    } 
  }
)

directives.directive('moveStatsTable', function() {
  function moveStatsController($scope, $attrs, StatsFetcher) {
    $scope.moveStatsList = [];
    $scope.setColor = function(isWhite) {
      if(this.refreshLock) {
        return
      }
      this.refreshLock = true
      this.moves = []
      this.isWhite = isWhite
      this.refreshMoveStatsList();
    }

    moveControl.setUsername = function(username) {
      this.username = username;
      this.moves = [];
      this.refreshMoveStatsList();
    }

    moveControl.removeLastNMoves = function(numMovesToRemove) {
      if(this.refreshLock) {
        return
      }
      this.refreshLock = true
      this.moves = this.moves.slice(0, numMovesToRemove*-1);
      this.refreshMoveStatsList();
    }

    moveControl.truncateMovesTo = function(lastIndex) {
      if(lastIndex >= this.moves.length) return
      if(this.refreshLock) {
        return
      }
      this.refreshLock = true
      this.moves = this.moves.slice(0, lastIndex);
      this.refreshMoveStatsList();
    }

    $scope.init = function(username) {
      moveControl.username = username;
      moveControl.refreshMoveStatsList()
    }
  }
  return {
    restrict: 'E', // this directive can only be used as the element
    // name of a DOM element. otherwise you could slap it on as an
    // attribute
    replace: true, // replace the template element with this custom
    // HTML tag
    templateUrl: 'directive_templates/move_stats_table.html',
    controller: moveStatsController
  }
});

directives.directive('navigationItem', ['$route', '$location', function($route, $location) {
  return {
    restrict: "E",
    replace: true,
    scope: true,
    template: '<div ng-click="goToRoute()"><p>{{ letter }}</p><div><p>{{ title }}</p></div></div>',
    link: function(scope, element, attrs) {
      scope.title = attrs.title;
      scope.letter = attrs.letter;
      scope.href = attrs.href;
      scope.goToRoute = function() {
        $location.path(scope.href);
      }
      $(element).hover(function() {
        $(element).children('div').stop(true, true).animate({
          left: 70
        }, 300);
      }, function() {
        $(element).children('div').stop(true, true).animate({
          left: (70 + 150)* -1
        }, 300);
      });
    }
  }
}]);
