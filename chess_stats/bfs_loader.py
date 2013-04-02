import logic


class BFSLoader(object):

	def __init__(self, starting_user, max_users_to_load=500):
		self.loaded_users = set()
		self.max_users_to_load = max_users_to_load
		self.queue = set([starting_user])

	def run(self):
		while self.queue and len(self.loaded_users) < self.max_users_to_load:
			current_user = self.queue.pop()
			user_games = logic.fetch_games_for_user(current_user)
			new_usernames = set()
			for game in user_games:
				new_usernames.add(game.black_username)
				new_usernames.add(game.white_username)
			self.loaded_users.add(current_user)
			print "loaded" + str(len(user_games)) + 'for ',
			print current_user + ' (' + str(len(self.loaded_users)) + ')'
			self.queue.update(new_usernames - self.loaded_users)
