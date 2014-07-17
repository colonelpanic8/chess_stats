import glob
import os

class ChessComPGNFileFinder(object):

    filename_matcher = re.compile('.*\.pgn')

    def get_matching_files(self, directory='.'):
        for directory_path, directory_names, filenames in os.walk(directory):
            for filename in filenames:
                if self.filename_matcher(filename):
                    yield os.path.join(directory_path, filename)

    def load(self, load_path=None, multi_game_pgns=False):
        if not load_path:
            load_path = self.DEFAULT_LOAD_PATH
            if not os.path.exists(load_path):
                raise ValueError("load_path does not exist")

        filenames = glob.glob(os.path.join(load_path, '*'))
        filenames = (filename for filename in filenames if re.match(".*\.pgn", filename))

        for filename in filenames:
            with open(filename) as pgn_file:
                yield pgn_file.read()
