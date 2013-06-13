var menuWidth = 70;

$(document).ready(function () {
  $("#navigation .links > div").hover(function(){
    $(this).children('div').stop(true, true).animate({
      left:menuWidth
    }, 300);
  },function(){
    $(this).children('div').stop(true, true).animate({
      left: (menuWidth+150)*-1
    }, 300);
  });
});

// angular.module('ChessStats.directives', []).directive(
//   'navigationItem', function() { 
//     return {
//       restrict: 'E',
//       link: function(scope, element, attrs) {
//         debugger;
//         $(element).hover(function(){
//           $(this).children('div').stop(true, true).animate({
//             left:menuWidth
//           }, 300);
//         },function(){
//           $(this).children('div').stop(true, true).animate({
//             left: (menuWidth+150)*-1
//           }, 300);
//         });
//       },
//       template: "<div class='navigation-link'>
// <p><a href="">4</a></p>
//             <div>
//               <p>Moves Statistics</p>
//             </div>
//           </div>",
//       scope: {
//         title: "@",
//         href: "@",
//         color: "@"
//       }
//     };
//   });
