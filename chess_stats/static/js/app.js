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
     $locationProvider.html5Mode(true);
     $routeProvider.when('/interactive_analysis', {
       templateUrl: "/static/js/view_templates/interactive_analysis.html",
       controller: InteractiveAnalysisCtrl
     }).when('/', {
       templateUrl: "/static/js/view_templates/enter_username.html",
       controller: InteractiveAnalysisCtrl
     }).otherwise({
       redirectTo: "/",
       templateUrl: "/static/js/view_templates/enter_username.html"
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
