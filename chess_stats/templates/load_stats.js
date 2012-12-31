var moves = []

var get_moves_stats = function(next_move) {
	$.get(
		'http://127.0.0.1:8000/chess_stats/get_stats',
		{'username': 'AlexMalison', 'moves': moves},
		function(data) {
			$('.result').html(data);
			var sorted_stats = JSON.parse(data)
			document.write('<table>');
			for(i=0; i<sorted_stats.length; i++) {
				document.write('<tr>');
				document.write('<td>');
				document.write(sorted_stats[i][0]);
				document.write('</td>');
				document.write('<td>');
				document.write(sorted_stats[i][1].white_wins);
				document.write('</td>');
				document.write('<td>');
				document.write(sorted_stats[i][1].draws);
				document.write('</td>');
				document.write('<td>');
				document.write(sorted_stats[i][1].black_wins);
				document.write('</td>');
				document.write('</tr>');
			}
			document.write('</table>');
		}
	)
}
