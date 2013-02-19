'use strict';


// Declare app level module which depends on filters, and services
angular.module(
    'myApp',
    ['myApp.filters', 'myApp.services', 'myApp.directives'],
    function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }
).
  config(
      [
          '$routeProvider',
          '$locationProvider',
          function($routeProvider, $locationProvider) {
              $locationProvider.html5Mode(true);
          }
      ]
  );
