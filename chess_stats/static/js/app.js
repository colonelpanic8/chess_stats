'use strict';

// Declare app level module which depends on filters, and services
var ChessStats = angular.module(
  'ChessStats',
  [
    'ChessStats.filters',
    'ChessStats.directives',
    'ChessStats.factories',
    'ChessGame'
  ]
).config(
  ['$routeProvider', '$locationProvider',
   function($routeProvider, $locationProvider) {
     //$locationProvider.html5Mode(true);
     $routeProvider.when('/:username/game_history', {
       templateUrl: "/static/js/view_templates/game_history.html",
       controller: GameHistoryCtrl
     }).when('/:username/rating_graph', {
       templateUrl: "/static/js/view_templates/rating_graph.html",
       controller: RatingGraphCtrl
     }).when('/interactive_analysis/:chessDotComID', {
       templateUrl: "/static/js/view_templates/interactive_analysis.html",
       controller: InteractiveAnalysisCtrl
     }).when('/:username/moves_analysis', {
       templateUrl: "/static/js/view_templates/moves_analysis.html",
       controller: MoveAnalysisCtrl
     }).when('/', {
       templateUrl: "/static/js/view_templates/enter_username.html",
       controller: LoginCtrl
     }).otherwise({
       redirectTo: "/"
     });
   }
  ]).run(['loadTemplates', function(loadTemplates) {
    loadTemplates("/static/js/lib/ChessBoard/src/templates/");
  }]);

ChessStats.directive('ngFade', function () {
  return function (scope, element, attrs) {
    element.css('display', 'none');
    scope.$watch(attrs.ngFade, function (value) {
      if (value) {
        element.fadeIn(500);
      } else {
        element.fadeOut(100);
      }
    });
  }
});
