from collections import namedtuple
import datetime
import re
import select
import subprocess


AnalysisInfo = namedtuple('AnalysisInfo', ["best_move", "centipawn_score", "continuation_string"])


class UCIClient(object):

    def __init__(self, process_command):
        self._process_command = process_command

    def __enter__(self):
        self.start_engine()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.quit()
        except Exception:
            pass

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

        if evaluation_lines:
            return self._parse_evaluation_lines(evaluation_lines)

    def start_engine(self):
        self._engine = subprocess.Popen(
            [self._process_command],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        self._engine.stdin.write("isready\n")
        while True:
            if self._engine.stdout.readline().rstrip() == 'readyok':
                return

    evaluation_line_matcher = re.compile("score cp (-?[0-9]*)")
    continuation_line_matcher = re.compile("pv ((:?[a-h][1-8][a-h][1-8])(:? [a-h][1-8][a-h][1-8])*)")
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
                continuation_string = self.continuation_line_matcher.search(line).group(1)
                break
        if centipawn_score is None:
            import ipdb; ipdb.set_trace()
        return AnalysisInfo(
            best_move, centipawn_score, continuation_string
        )

    def quit(self):
        print "quitting"
        self._engine.stdin.write("quit\n")


StockfishClient = lambda *args, **kwargs: UCIClient('./stockfish_osx', *args, **kwargs)


if __name__ == '__main__':
    print __file__
    uci_client = StockfishClient()
    import ipdb; ipdb.set_trace()
