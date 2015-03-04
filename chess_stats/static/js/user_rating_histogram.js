function buildDate(date) { 
  var dateString = date.year.toString() + '-' + date.month.toString() + '-' + date.day.toString();
  return dateString;
}

function averageEloByDate(userRatingElements) {
  var aggregateElo = 0;
  var maxId = 0;
  var maxIdElo = null;
  var minId = Infinity;
  var minIdElo = null;
  var numberOfElosInDay = 0;
  var previousDate = userRatingElements[0].date;
  var averageRatingByDate = [];
  _.each(userRatingElements, function(ratingElement) {
    if (ratingElement.date.valueOf() === previousDate.valueOf()) {
      if (ratingElement.chess_dot_com_id > maxId) {
        maxId = ratingElement.chess_dot_com_id;
        maxIdElo = ratingElement.elo;
      }
      if (ratingElement.chess_dot_com_id < minId) {
        minId = ratingElement.chess_dot_com_id;
        minIdElo = ratingElement.elo;
      }
      numberOfElosInDay += 1;
      aggregateElo = aggregateElo + ratingElement.elo;
    } else {
      averageRatingByDate.push({averageElo: aggregateElo/numberOfElosInDay, date: previousDate, eodElo: maxIdElo, bodElo: minIdElo})
      minId = ratingElement.chess_dot_com_id;
      minIdElo = ratingElement.elo;
      maxId = ratingElement.chess_dot_com_id;
      maxIdElo = ratingElement.elo;
      aggregateElo = ratingElement.elo;
      previousDate = ratingElement.date;
      numberOfElosInDay = 1;
    }
  });
  if(numberOfElosInDay > 0) averageRatingByDate.push(
    {averageElo: aggregateElo/numberOfElosInDay, date: previousDate, eodElo: maxIdElo, bodElo:minIdElo}
  );
  return averageRatingByDate;
}


// define dimensions of graph
var m = [80, 10, 80, 100]; // margins
var w = 1200 - m[1] - m[3]; // width
var h = 600 - m[0] - m[2]; // height

angular.module('ChessStats.directives').directive('userRatingHistogram', function() { 
  return function(scope, element, attrs) {
    $.ajax({
      url: '/user_rating_history_json/' + attrs.username,
      method: 'get',
      datatype: 'json',
      success: function(userRatingElementsJSON) {
        var userRatingElements = JSON.parse(userRatingElementsJSON);
        _.each(userRatingElements, function (ratingElement) {
          ratingElement.date = new Date(buildDate(ratingElement.date_played));
        });
        userRatingElements = _.sortBy(userRatingElements, function(item) {return item.date});
        var averagedEloByDate = averageEloByDate(userRatingElements);
        var data = _.map(userRatingElements, function(ratingElement) {
          return [ratingElement.date, ratingElement.elo];
        });
        var startTime = _.min(data, function(item) { return item[0] })[0];
        var endTime = _.max(data, function(item) { return item[0] })[0];
        var minY = _.min(data, function(item) { return item[1] })[1];
        var maxY = _.max(data, function(item) { return item[1] })[1];
        
        var x = d3.time.scale().domain([startTime, endTime]).range([0, w]);
        x.tickFormat(d3.time.format("%Y-%m-%d"));
        var y = d3.scale.linear().domain([minY, maxY]).range([h, 0]);
        
        var averageLine = d3.svg.line()
            .x(function(ratingElement, index) {
              return x(ratingElement.date); 
            })
            .y(function(ratingElement) { 
              return y(ratingElement.averageElo);
            })
        var eodLine = d3.svg.line()
            .x(function(ratingElement, index) {
              return x(ratingElement.date); 
            })
            .y(function(ratingElement) { 
              return y(ratingElement.eodElo);
            })
        var bodLine = d3.svg.line()
            .x(function(ratingElement, index) {
              return x(ratingElement.date); 
            })
            .y(function(ratingElement) { 
              return y(ratingElement.bodElo);
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

        // Add the x-axis label
        graph.append("text")
          .attr("id", "x-axis-label") 
          .attr("transform", "translate(" + (w / 2) + " ," + (h + m[3]/2) + ")")
          .style("text-anchor", "middle")
          .text("Game Date" + " (" + new Date().getFullYear() + ")");

        // Create left yAxis
        var yAxisLeft = d3.svg.axis().scale(y).orient("left");
        // Add the y-axis to the left
        graph.append("svg:g")
          .attr("class", "y axis")
          .attr("transform", "translate(-10,0)")
          .call(yAxisLeft);

        // Add the y-axis label
        graph.append("text")
          .attr("id", "y-axis-label") 
          .attr("transform", "rotate(-90)")
          .attr("y", 0 - m[0])
          .attr("x", 0 - (h / 2))
          .style("text-anchor", "middle")
          .text("Player Rating (elo)");

        var tooltipDiv = d3.select("body").append("div")   
            .attr("class", "tooltip")               
            .style("opacity", 0);

        graph.append("svg:path").attr("d", averageLine(averagedEloByDate)).attr("class", "graph-line").attr("class", "average");
        graph.append("svg:path").attr("d", eodLine(averagedEloByDate)).attr("class", "graph-line").attr("class", "eod");
        graph.append("svg:path").attr("d", bodLine(averagedEloByDate)).attr("class", "graph-line").attr("class", "bod");
        graph.selectAll("circle")
          .data(userRatingElements)
          .enter()
          .append("circle")
          .attr("class", "graph-circle")
          .attr("cx", function(ratingElement, index) {
            return x(ratingElement.date);
          })
          .attr("cy", function(ratingElement) {
            return y(ratingElement.elo);
          })
          .attr("r", 3.5)
          .on("mouseover", function(ratingElement) {      
            tooltipDiv.transition()        
              .duration(200)      
              .style("opacity", .8);      
            tooltipDiv .html( "Your ELO: " + ratingElement.elo + "<br/>"
                              + "Opp ELO: " + ratingElement.opponent_elo + "<br/>" + "Opp: " + ratingElement.opponent)
              .style("left", (d3.event.pageX) + "px")     
              .style("top", (d3.event.pageY - 70) + "px");    
          })                  
          .on("mouseout", function(ratingElement) {       
            tooltipDiv.transition()        
              .duration(500)      
              .style("opacity", 0);   
          })
          .on('click', function (ratingElement) {
            window.location = 'http://www.chess.com/livechess/game?id=' +
              ratingElement.chess_dot_com_id.toString()
          });
      }
    });
  }
});
