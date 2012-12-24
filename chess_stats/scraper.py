from contextlib import closing
from urllib import urlopen
import os
import re

from BeautifulSoup import BeautifulSoup


class ChessComScraper(object):

	ARCHIVE_BASE_PAGE_FORMAT = "home/game_archive?member={member}&show={game_type}"
	BASE_URL = "http://www.chess.com/"
	GAME_LINK_HTML_ELEMENT_FORMAT_STRING = "c14_row{row}_7"
	GAME_LINK_RE_MATCH_STRING = "/{game_type}/game\?id=([0-9]*)"
	PGN_LINK_FORMAT = '{base_url}{game_type}/download_pgn.html?lid={game_id}'

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

	def __init__(self, game_type, log_function=None):

		self.game_ids = []
		self.soup = None
		self.game_type = game_type
		if log_function is None:
			def log(string):
				print string
			log_function = log
		self.log_function = log_function

	def scrape(self, member, stop_at_id=None):
		"""Scrape the chess.com games of member. Inserts the member name into self.game_ids
		before all the ids associated with a member.
		This means that scrape can be executed multiple times on different member names,
		and we can pass the member id on to the pgn parser tools.
		"""

		with closing(urlopen(
			self.BASE_URL + self.ARCHIVE_BASE_PAGE_FORMAT.format(
				member=member,
				game_type=self.GAME_TYPES_SHOW[self.game_type]
			)
		)) as html:
			self.soup = BeautifulSoup(html.read())

		self.game_ids.append(member)

		while self.parse_page(stop_at_id=stop_at_id) and self.find_next_page():
			pass

	def parse_page(self, stop_at_id=None):
		"""Parse a single page of a game archive from chess.com."""

		row = 0
		while True:
			game_id = self.get_game_id(row)
			if game_id is None:
				self.log_function("No more games found on page.")
				return True
			elif game_id == stop_at_id:
				return False
			else:
				self.game_ids.append(game_id)
			row += 1

	def find_next_page(self):
		"""Find the next page from the html of the current page.
		Returns True on success and False on failure.
		"""

		pagination_find = self.soup.find(name = "ul", attrs={"class" : "pagination"})
		if pagination_find:
			links = pagination_find.findAll(name = "a")
			for link in links:
				if re.match('^Next', link.contents[0]):
					with closing(urlopen(self.BASE_URL + link['href'])) as html:
						self.soup = BeautifulSoup(html.read())
						return True
			self.log_function('Could not find a "Next" link.')
			return False
		else:
			self.log_function("Could not find pagination.")
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
			self.log_function("Could not match game link string")
			return None

		return game_id

	def get_pgns(self):
		"""Return a generator which yields pgns together with its associated game_id and member"""

		# The first item in game_ids should always be a member string. If not the member variable
		# will not be defined when we yield the first item
		assert isinstance(self.game_ids[0], str)

		for game_id in self.game_ids:
			if isinstance(game_id, str):
				member = game_id
			else:
				yield (game_id, member, self.get_pgn_string(game_id))

	def get_pgn_string(self, game_id):
		"""Download the pgn associated with game_id from chess.com"""

		# I don't know why, but it seems that chess.com always uses echess in this case,
		# even for live games
		url = self.PGN_LINK_FORMAT.format(
			base_url=self.BASE_URL,
			game_type='echess',
			game_id=game_id
		)
		with closing(urlopen(url)) as pgn_file:
			return pgn_file.read()


class ChessComPGNFileLoader(object):

	DEFAULT_LOAD_PATH = './load'

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
