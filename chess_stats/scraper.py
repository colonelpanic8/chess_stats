from contextlib import closing
from urllib import urlopen
import glob
import itertools
import logging
import os
import re

from BeautifulSoup import BeautifulSoup



class ChessDotComScraper(object):

    ARCHIVE_BASE_PAGE_FORMAT = "home/game_archive?member={member}&show={game_type}"
    BASE_URL = "http://www.chess.com/"
    GAME_LINK_HTML_ELEMENT_FORMAT_STRING = "c14_row{row}_7"
    GAME_LINK_RE_MATCH_STRING = "/{game_type}/game\?id=([0-9]*)"

    GAME_TYPE_LIVE = 0
    GAME_TYPE_ONLINE = 1

    GAME_TYPES_SHOW = {
        GAME_TYPE_LIVE: "live",
        GAME_TYPE_ONLINE: "echess"
    }

    GAME_TYPES_PATH = {
        GAME_TYPE_LIVE: "livechess",
        GAME_TYPE_ONLINE: "echess"
    }

    def __init__(self, game_type, member, logger=None):
        self.member = member
        self.game_ids = []
        self.soup = None
        self.game_type = game_type
        self.done = False
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(10)

    def scrape(self, stop_at_id=None):
        with closing(urlopen(
                self.BASE_URL + self.ARCHIVE_BASE_PAGE_FORMAT.format(
                    member=self.member,
                    game_type=self.GAME_TYPES_SHOW[self.game_type]))) as html:
            self.soup = BeautifulSoup(html.read())
            while not self.done:
                for game_id in self.parse_page(stop_at_id=stop_at_id):
                    yield game_id
                self.done = not self.find_next_page()

    def parse_page(self, stop_at_id=None):
        """Parse a single page of a game archive from chess.com. Returns true if
        stop_at_id was encountered."""
        for row in itertools.count():
            self.logger.debug("Getting row {0}".format(row))
            game_id = self.get_game_id(row)
            if game_id is None:
                self.logger.debug("No more games found on page.")
                break
            elif game_id == stop_at_id:
                self.done = True
                break
            else:
                self.game_ids.append(game_id)
                yield game_id

    def find_next_page(self):
        """Find the next page from the html of the current page. Returns True on
        success and False on failure.
        """
        pagination_find = self.soup.find(
            name="ul",
            attrs={"class" : "pagination"}
        )
        if pagination_find:
            links = pagination_find.findAll(name = "a")
            for link in links:
                if re.match('^Next', link.contents[0]):
                    self.logger.debug(
                        'Now at {new_url}.'.format(new_url=link['href'])
                    )
                    with closing(urlopen(self.BASE_URL + link['href'])) as html:
                        self.logger.debug(
                            'Now at {new_url}.'.format(new_url=link['href'])
                        )
                        self.soup = BeautifulSoup(html.read())
                        return True
                        self.logger.debug('Could not find a "Next" link.')
                        return False
        else:
            self.logger.debug("Could not find pagination.")
            return False

    def get_game_id(self, row):
        """Get one game id from the current page at the row stored in row."""

        find_results = self.soup.find(
            name='td',
            id=self.GAME_LINK_HTML_ELEMENT_FORMAT_STRING.format(row=row)
        )
        if not find_results:
            return None

        game_url = find_results.contents[0]['href']

        re_match_string = self.GAME_LINK_RE_MATCH_STRING.format(
            game_type=self.GAME_TYPES_PATH[self.game_type]
        )
        match = re.search(
            re_match_string,
            game_url
        )
        if match:
            game_id = int(match.group(1))
        else:
            self.logger.debug("Could not match game link string")
            return None

        return game_id


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