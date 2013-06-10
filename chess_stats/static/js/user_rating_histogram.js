/* implementation heavily influenced by http://bl.ocks.org/1166403 */

function buildMorrisDate(date) { 
  var dateString = date.year.toString() + '-' + date.month.toString() + '-' + date.day.toString();
  return dateString;
}

function averageEloByDate(userRatingElements) {
  var aggregateElo = 0;
  var numberOfElosInDay = 0;
  var previousDate = userRatingElements[0].date;
  var averageRatingByDate = [];
  _.each(userRatingElements, function(ratingElement) {
    if (ratingElement.date.valueOf() === previousDate.valueOf()) {
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

// define dimensions of graph
var m = [80, 80, 80, 80]; // margins
var w = 1500 - m[1] - m[3];// width
var h = 600 - m[0] - m[2]; // height
var timeStep = 300000000;

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
            ratingElement.date = new Date(buildMorrisDate(ratingElement.date_played));
          });
          userRatingElements = _.sortBy(userRatingElements, function(item) {return item.date});
          var averagedEloByDate = averageEloByDate(userRatingElements);
          console.log(averagedEloByDate);
          var data = _.map(userRatingElements, function(ratingElement) {
            return [ratingElement.date, ratingElement.elo];
          });
          var startTime = _.min(data, function(item) { return item[0] })[0];
          var endTime = _.max(data, function(item) { return item[0] })[0];
          var minY = _.min(data, function(item) { return item[1] })[1];
          var maxY = _.max(data, function(item) { return item[1] })[1];
          console.log([minY, endTime]);
          _.each(data, function (item) {console.log(item[0])});
          
          var x = d3.time.scale().domain([startTime, endTime]).range([0, w]);
          x.tickFormat(d3.time.format("%Y-%m-%d"));
          var y = d3.scale.linear().domain([minY, maxY]).range([h, 0]);
          
          var line = d3.svg.line()
            .x(function(ratingElement, index) {
              return x(ratingElement.date); 
            })
            .y(function(ratingElement) { 
              return y(ratingElement.elo);
            })
          // Add an SVG element with the desired dimensions and
          // margin.
          var graph = d3.select(element[0]).append("svg:svg")
            .attr("width", w + m[1] + m[3])
            .attr("height", h + m[0] + m[2])
            .append("svg:g")
            .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

          // create yAxis
          var xAxis = d3.svg.axis().scale(x).tickSize(-h).tickSubdivide(1);

          // Add the x-axis.
          graph.append("svg:g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + h + ")")
            .call(xAxis);

          // create left yAxis
          var yAxisLeft = d3.svg.axis().scale(y).ticks(6).orient("left");
          // Add the y-axis to the left
          graph.append("svg:g")
            .attr("class", "y axis")
            .attr("transform", "translate(-10,0)")
            .call(yAxisLeft);
          
          // add lines
          // do this AFTER the axes above so that the line is above the
          // tick-lines
          console.log();
          graph.append("svg:path").attr("d", line(averagedEloByDate)).attr("class", "data1");
          graph.append("svg:path").attr("d", line(userRatingElements)).attr("class", "data2");
        }
      });
    }
  }
)
