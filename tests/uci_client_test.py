import testify as T
from chess_stats.uci_client import UCIClient


class UCIClientTestCase(T.TestCase):

    sample_analysis_string = "info depth 21 seldepth 36 score cp -24 nodes 33206425 nps 4050057 time 8199 multipv 1 pv e7e6 d2d4 d7d5 e4d5 e6d5 g1f3 g8f6 f1d3 f8d6 e1g1 e8g8 c2c4 d5c4 d3c4 b8c6 b1c3 c8f5 a2a3 c6a5 c4a2 a5c6 b2b4 f8e8 f3g5 e8e7 b4b5 c6a5"

    def test_continuation_line_matches(self):
        match = UCIClient.continuation_line_matcher.search(self.sample_analysis_string)
        assert match
        T.assert_equal(
            ["e7e6", "d2d4", "d7d5", "e4d5", "e6d5", "g1f3", "g8f6", "f1d3", "f8d6", "e1g1", "e8g8", "c2c4", "d5c4", "d3c4", "b8c6", "b1c3", "c8f5", "a2a3", "c6a5", "c4a2", "a5c6", "b2b4", "f8e8", "f3g5", "e8e7", "b4b5", "c6a5"],
            match.group(1).split(" ")
        )