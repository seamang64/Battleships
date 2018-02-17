import re
import logging
from channels import Group
from channels.sessions import channel_session
from .models import Game, Cell
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
log = logging.getLogger(__name__)
from django.utils.decorators import method_decorator

from channels.generic.websockets import JsonWebsocketConsumer

#========================================
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#MOST OF THIS IS THE SAME AS THE TUTORIAL
#PROBABLY CANT RUN I WILL TRY AND GET IT
#WORKING WHEN I KNOW MORE ABOUT WHAT IS
#NEEDED TO BE ADDED OR CHANGED
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#========================================

class LobbyConsumer(JsonWebsocketConsumer):

	# Set to True to automatically port users from HTTP cookies
	# (you don't need channel_session_user, this implies it)
	http_user = True


	def connection_groups(self, **kwargs):
		"""
		Called to return the list of groups to automatically add/remove
		this connection to/from.
		"""
		print("adding to connection group lobby")
		return ["lobby"]

	def connect(self, message, **kwargs):
		"""
		Perform things on connection start
		"""
		pass

	def receive(self, content, **kwargs):
		"""
		Called when a message is received with either text or bytes
		filled out.
		"""
		channel_session_user = True

		action = content['action'] #MADE SOME CHANGES HERE SO HOPEFULLY WONT BREAK
		if action == 'create_game':
			return Game.create_new(self.message.user, content['cols'], content['rows'])
			
		if action = 'find_game':
			return Game.get_available_games()

	def disconnect(self, message, **kwargs):
		"""
		Perform things on connection close
		"""
		pass

class GameConsumer(JsonWebsocketConsumer):
	# Set to True to automatically port users from HTTP cookies
	# (you don't need channel_session_user, this implies it)
	http_user = True

	def connection_groups(self, **kwargs):
		"""
		Called to return the list of groups to automatically add/remove
		this connection to/from.
		"""
		return ["game-{0}".format(kwargs['game_id'])]

	def connect(self, message, **kwargs):
		"""
		Perform things on connection start
		"""
		pass

	def receive(self, content, **kwargs):
		"""
		Called when a message is received with either text or bytes
		filled out.
		"""
		channel_session_user = True
		action = content['action']

		if action == 'hit_cell': #should set a cell's state
			Cell.set_cell(content['game_id'], content['row'], content['col'], content['player_num'], content['state'])

		if action == 'check_cell': #should return the state of a cell
			return Cell.get_cell_state(content['game_id'], content['row'], content['col'], content['player_num'])
			
		if action == 'get_turn': #should return the number of the player whose turn it is, 1 for player one, 2 for player 2
			game = Game.get_game(content['game_id'])
			return game.player_turn
			
		if action == 'end_turn': #ends the current turn and switches the current turn to the other player
			Game.set_next_turn(current_game)
			
		if action == 'get_winner': 
		#can be used to check if a player has been declared as the winner, 0: no winner, 1:player 1 wins, 2: player 2 wins
			game = Game.get_game(content['game_id'])
			return game.winner
			
		if action == 'set_winner': #sets the winner of a game, 1 for player 1, 2 for player 2
			Game.set_winner(content['game_id'], content['player_num'])

	def disconnect(self, message, **kwargs):
		"""
		Perform things on connection close
		"""
		pass
