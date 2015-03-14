angular.module('ChessStats.directives').directive('performanceByOppElo', function(performanceByOppEloFetcher) {
  return function(scope, element, attrs) {
    performanceByOppEloFetcher(attrs.username, function(ratingData) {
      var margin = {top: 20, right: 100, bottom: 30, left: 40},
	  width = 960 - margin.left - margin.right,
	  height = 500 - margin.top - margin.bottom;

      var x = d3.scale.linear()
	    .rangeRound([0, width]);

      var y = d3.scale.linear()
	    .rangeRound([height, 0]);

      var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");

      var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .tickFormat(d3.format(".0%"));

      var area = d3.svg.area()
	    .x(function(d) { return x(d.x); })
	    .y0(function(d) { return y(d.y0); })
	    .y1(function(d) { return y(d.y0 + d.y); });

      var svg = d3.select(element[0]).append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	    .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var color = d3.scale.category20();
      color.domain(["win", "loss", "draw"]);

      var stack = d3.layout.stack()
	    .values(function(d) { return d.values; });

      var winValues = [];
      var drawValues = [];
      var lossValues = [];


      _.each(ratingData, function (ratingBucketInfo) {
	var averageRating = (ratingBucketInfo.min_elo + ratingBucketInfo.max_elo)/2;
	winValues.push({
	  x: averageRating,
	  y: ratingBucketInfo.stats.user_win_pct
	});

	drawValues.push({
	  x: averageRating,
	  y: ratingBucketInfo.stats.draw_pct
	});

	lossValues.push({
	  x: averageRating,
	  y: ratingBucketInfo.stats.opp_win_pct
	});
      });

      var stacked = stack([{type: "win", values: winValues}, {type: "loss", values: lossValues}, {type: "draw", values: drawValues}]);
      var maxX = winValues[winValues.length-1].x;
      console.log(stacked);
      console.log([winValues[0].x, winValues[winValues.length-1].x]);
      x.domain([winValues[0].x, winValues[winValues.length-1].x]);
      y.domain([0, 1]);

      var bucketedWinLoss = svg.selectAll(".bucketed")
	    .data(stacked)
	    .enter().append("g")
	    .attr("class", "bucketed");

      bucketedWinLoss.append("path")
	.attr("class", "area")
	.attr("d", function(d) { return area(d.values); })
	.style("fill", function(d) { return color(d.type); });

      bucketedWinLoss.append("text")
	.datum(function(d) { return {name: d.type, value: maxX}; })
	.attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.value.y0 + d.y / 2) + ")"; })
	.attr("x", -6)
	.attr("dy", ".35em")
	.text(function(d) { return d.type; });

      svg.append("g")
      	.attr("class", "x axis")
      	.attr("transform", "translate(0," + height + ")")
      	.call(xAxis);

      svg.append("g")
      	.attr("class", "y axis")
      	.call(yAxis);
    });
  };
});
