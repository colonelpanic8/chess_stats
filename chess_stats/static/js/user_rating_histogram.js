function buildMorrisDate(date) { 
  var dateString = date.year.toString() + '-' + date.month.toString() + '-' + date.day.toString();
  return dateString;
}

function averageEloByDate(userRatingElements) {
  var aggregateElo = 0;
  var numberOfElosInDay = 0;
  var previousDate = userRatingElements[0].date
  var averageRatingByDate = [];
  _.each(userRatingElements, function(ratingElement) {
    if (ratingElement.date === previousDate) {
      numberOfElosInDay += 1;
      aggregateElo = aggregateElo + ratingElement.elo;
    } else {
      averageRatingByDate.push({elo: aggregateElo/numberOfElosInDay, date: previousDate})
      aggregateElo = ratingElement.elo;
      previousDate = ratingElement.date;
      numberOfElosInDay = 1;
    }
  });
  return averageRatingByDate;
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
          averageRatingByDate = averageEloByDate(userRatingElements);
          console.log(averageRatingByDate);
          Morris.Line({
            element: element,
            data: averageRatingByDate,
            xkey: 'date',
            ykeys: ['elo'],
            ymax: _.max(averageRatingByDate, function(ratingElement) {
              return ratingElement.elo;
            }).elo,
            ymin: _.min(averageRatingByDate, function(ratingElement) {
              return ratingElement.elo
            }).elo
          });
        }
      });
    }
  }
)


angular.module('ChessStats.directives', []).directive(
  'ngUserRatingHistogramByGame', function() { 
    return function(scope, element, attrs) {
      $.ajax({
        url: '/user_rating_history_json/' + attrs.username,
        method: 'get',
        datatype: 'json',
        success: function(userRatingElementsJSON) {
          var userRatingElements = JSON.parse(userRatingElementsJSON);
          var gameIndex = 0;
          _.each(userRatingElements, function (ratingElement) {
            ratingElement.date = buildMorrisDate(ratingElement.date_played);
            ratingElement.x = gameIndex;
            gameIndex += 1;
          });
          Morris.Line({
            element: element,
            data: userRatingElements,
            xkey: 'x',
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
