import datetime
import re
import select
import subprocess


class UCIClient(object):

    def __init__(self, process_command):
        self._process_command = process_command
        self._engine = self._start_engine()
        self._engine.stdin.write("isready\n")
        while True:
            # WHAT!? This is shit code:
            if self._engine.stdout.readline().rstrip() == 'readyok':
                break

    def set_position_from_moves_list(self, uci_moves_list):
        self._engine.stdin.write(
            "position startpos moves %s\n" % ' '.join(uci_moves_list)
        )
        return self

    def start_position_evaluation(self, duration=datetime.timedelta(seconds=5)):
        self._engine.stdin.write(
            "go movetime %d\n" % int(duration.total_seconds()*1000)
        )

    def maybe_read_evaluation(self):
        evaluation_lines = []
        while select.select([self._engine.stdout], [], [], .3)[0]:
            data = self._engine.stdout.readline().rstrip()
            if data is not None:
                evaluation_lines.append(data)

        return self._parse_evaluation_lines(evaluation_lines)

    def _start_engine(self):
        return subprocess.Popen(
            [self._process_command],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )

    evaluation_line_matcher = re.compile("score cp (-?[0-9]*)")
    best_move_line_matcher = re.compile("bestmove ([a-z0-9]*)")

    def _parse_evaluation_lines(self, evaluation_lines):
        centipawn_score = None
        best_move = ''
        match = self.best_move_line_matcher.match(evaluation_lines.pop())
        if match:
            best_move = match.group(1)
        for line in evaluation_lines[::-1]:
            match = self.evaluation_line_matcher.search(line)
            if match and match.group(1) != '':
                centipawn_score = int(match.group(1))
                break
        if centipawn_score is None:
            import ipdb; ipdb.set_trace()
        return best_move, centipawn_score

    def quit(self):
        self._engine.stdin.write("quit\n")


StockfishClient = lambda *args, **kwargs: UCIClient('stockfish_osx', *args, **kwargs)


if __name__ == '__main__':
    print __file__
    uci_client = StockfishClient()
    import ipdb; ipdb.set_trace()
