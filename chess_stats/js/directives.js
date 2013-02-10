'use strict';

/* Directives */


angular.module('myApp.directives', []).
  directive('appVersion', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]);

angular.module('myApp.directives', []).directive(
    'jq:animate',
    function(jQueryExpression, templateElement){ 
        return function(instanceElement){ 
            instanceElement.show('slow'); 
        } 
    }
);
