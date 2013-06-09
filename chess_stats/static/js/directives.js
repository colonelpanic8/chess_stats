'use strict';

/* Directives */

angular.module('ChessStats.directives', []).directive(
    'jqAnimate',
    function(jQueryExpression, templateElement){ 
        console.log('init')
        return function(instanceElement){
            console.log('test')
            instanceElement.show('slow'); 
        } 
    }
)



