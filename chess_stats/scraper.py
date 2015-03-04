import itertools
import logging
import re

from BeautifulSoup import BeautifulSoup
import requests


class ChessDotComPageScraper(object):

    GAME_TYPE_LIVE = 0
    GAME_TYPE_ONLINE = 1

    GAME_TYPES_PATH = {
        GAME_TYPE_LIVE: "livechess",
        GAME_TYPE_ONLINE: "echess"
    }

    GAME_LINK_HTML_ELEMENT_FORMAT_STRING = "c14_row{row}_7"
    GAME_LINK_RE_MATCH_STRING = "/{game_type}/game\?id=([0-9]*)"

    def __init__(self, html, game_type, stop_at_id=None, logger=None):
        self.soup = BeautifulSoup(html)
        self.stop_at_id = stop_at_id
        self.logger = logger
        self.game_type = game_type

    def parse_page(self):
        """Parse a single page of a game archive from chess.com. Returns true if
        stop_at_id was encountered."""
        for row in itertools.count():
            self.logger.debug("Getting row {0}".format(row))
            game_id = self.get_game_id(row)
            if game_id is None:
                self.logger.debug("No more games found on page.")
                break
            elif game_id == self.stop_at_id:
                break
            else:
                yield game_id

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
        match = re.search(re_match_string, game_url)
        if match:
            game_id = int(match.group(1))
        else:
            self.logger.debug("Could not match game link string")
            return None

        return game_id

    @staticmethod
    def intable(value):
        try:
            int(value)
        except:
            return False
        else:
            return True

    @property
    def max_page_number(self):
        pagination_find = self.soup.find(name="ul", attrs={"class": "pagination"})
        if pagination_find:
            page_numbers = [int(item.text)
                            for item in pagination_find.findAll(name="a") if self.intable(item.text)]
            if page_numbers:
                return max(page_numbers)
            return 0
        else:
            self.logger.debug("Could not find pagination.")
            self.logger.debug("Max pagination was.")
            raise Exception()


class ChessDotComScraper(object):

    ARCHIVE_BASE_PAGE_URL = "home/game_archive"
    BASE_URL = "http://www.chess.com/"

    GAME_TYPE_LIVE = 0
    GAME_TYPE_ONLINE = 1

    GAME_TYPES_SHOW = {
        GAME_TYPE_LIVE: "live",
        GAME_TYPE_ONLINE: "echess"
    }

    def __init__(self, game_type, member, logger=None):
        self.member = member
        self.game_type = game_type
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(10)

    def scrape(self, stop_at_id=None):
        for page_number in itertools.count(1):
            self.logger.debug("Getting Page {0}".format(page_number))
            page_scraper = ChessDotComPageScraper(self.get_page(page_number),
                                                  self.game_type,
                                                  logger=self.logger,
                                                  stop_at_id=stop_at_id)
            self.logger.debug("Max page number is {0}".format(
                page_scraper.max_page_number
            ))
            if page_scraper.max_page_number < page_number:
                break
            for game_id in page_scraper.parse_page():
                yield game_id

    def get_page(self, page_number=None):
        params = {
            'member': self.member,
            'show': self.GAME_TYPES_SHOW[self.game_type]
        }
        if page_number is not None:
            params['page'] = page_number
        request = requests.get(self.BASE_URL + self.ARCHIVE_BASE_PAGE_URL,
                               params=params)
        if request.status_code != 200:
            self.logger.debug("Non 200 response from chess.com.")
            raise Exception
        return request.text



