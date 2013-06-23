'use strict';

// Declare app level module which depends on filters, and services
var ChessStats = angular.module(
    'ChessStats',
    [
        'ChessStats.filters',
        'ChessStats.services',
        'ChessStats.directives',
        'ChessStats.factories',
        'ChessGame'
    ]
).config(
    [
        '$routeProvider',
        '$locationProvider',
        function($routeProvider, $locationProvider) {
            $locationProvider.html5Mode(true);
        }
    ]
);

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
