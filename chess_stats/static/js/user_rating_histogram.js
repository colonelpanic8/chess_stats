function buildMorrisDate(date) { 
  var dateString = date.year.toString() + '-' + date.month.toString() + '-' + date.day.toString();
  console.log(dateString);
  return dateString;
}

angular.module('ChessStats.directives', []).directive(
  'ngUserRatingHistogram', function() { 
    return function(scope, element, attrs) {
      $.ajax({
        url: '/user_rating_history_json/' + attrs.username,
        method: 'get',
        datatype: 'json',
        success: function(userRatingElementsJSON) {
          var userRatingElements = JSON.parse(userRatingElementsJSON);
          _.each(userRatingElements, function (ratingElement) {
            ratingElement.date = buildMorrisDate(ratingElement.date_played);
          });
          console.log(userRatingElements);
          Morris.Line({
            element: element,
            data: userRatingElements,
            xkey: 'date',
            ykeys: ['elo'],
            ymax: _.max(userRatingElements, function(ratingElement) {
              return ratingElement.elo;
            }).elo,
            ymin: _.min(userRatingElements, function(ratingElement) {
              return ratingElement.elo
            }).elo
          });
        }
      });
    }
  }
)
