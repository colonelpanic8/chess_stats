'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', ['ngResource']).
	value('version', '0.1').
	factory('Chess', ['$resource', function($resource){
		return $resource('/chess_stats/get_stats', 
						 {username: 'AlexMalison', moves: []}, 
						 {get: {method: "GET"}})
	}]);
