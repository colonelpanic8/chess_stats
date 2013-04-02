'use strict';


// Declare app level module which depends on filters, and services
var ChessStats = angular.module(
    'ChessStats',
    [
    	'ChessStats.filters',
    	'ChessStats.services',
    	'ChessStats.directives'
    ],
    function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }
).config(
    [
        '$routeProvider',
        '$locationProvider',
        function($routeProvider, $locationProvider) {
            $locationProvider.html5Mode(true);
        }
    ]
);

ChessStats.directive(
    'jqAnimate',
    function(jQueryExpression, templateElement){ 
        console.log('init')
        return function(instanceElement){
            console.log('test')
            instanceElement.show('slow'); 
        } 
    }
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
