from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from django.contrib.auth.models import User
import json
import random
from asgiref.sync import async_to_sync
from .models import Game, User, User_Shipyard, Battleships_User, Cell, Bot_Moves
from .serializers import *
import ast
from channels.layers import get_channel_layer


class LobbyConsumer(WebsocketConsumer):

	http_user = True
	
	def connect(self):
		self.room_name = 'lobby'
		self.room_group_name = 'game'
		
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)
		
		self.accept()

	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)

	def receive(self, text_data, **kwargs):
		channel_session_user = True
		content = ast.literal_eval(text_data)
		action = content['action']
		
		if action == 'create_game':
			player = User.objects.get(username=ast.literal_eval(text_data)['player'])
			shipyard = content['shipyard']
			max = int(shipyard[0]) + int(shipyard[1]) + int(shipyard[2]) + int(shipyard[3]) + int(shipyard[4])
			#creates the game and sets the players turn
			game = Game.create_new_game(player, content['height'], content['width'], max, content['shipyard'],False)
			game.player_turn=(random.randint(1,2))
			game.save
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'new_game',
					'player': game.p1.username,
					'game': game.id
				}
			)
		
		if action == 'create_bot_game':
			player = User.objects.get(username=ast.literal_eval(text_data)['player'])
			shipyard = content['shipyard']
			max = int(shipyard[0]) + int(shipyard[1]) + int(shipyard[2]) + int(shipyard[3]) + int(shipyard[4])
			#creates the game
			game = Game.create_new_game(player, content['height'], content['width'], max, content['shipyard'],True)
			#creates a new bot
			i = 0
			while User.objects.filter(username='bot{0}'.format(i)).exists():
				i+=1
			user = User.objects.create_user('bot{0}'.format(i))
			#sets the bot as player 2
			game.p2=user
			game.save()
			Cell.create_new_board(game.id, game.num_rows, game.num_cols, game.p1, game.p2)
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'new_game',
					'player': game.p1.username,
					'game': game.id
				}
			)
			
			
		if action == 'delete_game':
			game = Game.get_game(content['game_id'])
			if game.bot_game:
				Bot_Moves.delete_game(content['game_id'])
			Game.delete_game(content['game_id'],self.scope['user'])

		if action == 'find_game':
			return Game.get_available_games()
		
		if action == 'create_board':
			Cell.create_new_board(content['game_id'], content['rows'], content['cols'], content['p1_id'], content['p2_id'])
		
		if action == 'get_ships_list':
			return Shipyard.get_all_ships()
			
		if action == 'join_game':
			player = User.objects.get(username=ast.literal_eval(text_data)['player'])
			Game.add_p2(content['game_id'], player)
			User_Shipyard.delete_all_user_ships(player)
			
		if action == 'create_user':
			User.create_new_user(content['username'])
		
		if action == 'delete_user':
			User.delete_user(content['user_id'])
		
		if action == 'get_user_shipyard_size':
			return get_user_shipyard_size(content['user_id'])
		
	def new_game(self, event):
		avail_game_list = Game.get_available_games()
		avail_serializer = GameSerializer(avail_game_list, many=True)
		other_data = {'player': event['player'], 'game': event['game']}
		self.send(text_data=json.dumps(avail_serializer.data))
		self.send(text_data=json.dumps(other_data))
	
	def update(self, event):
		self.send(text_data=json.dumps({'instruction': 'update'}))
		

class GameConsumer(JsonWebsocketConsumer):
	
	http_user = True

	def connect(self, **kwargs):
		self.room_group_name = 'user-' + str(self.scope['user'].id)
		
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)
		
		self.accept()
		
		async_to_sync(self.channel_layer.group_send)('user-' + str(self.scope['user'].id),{'type': 'update'})
		async_to_sync(self.channel_layer.group_send)('game',{'type': 'update'})
		
	def receive(self, text_data, **kwargs):
	
		channel_session_user = True
		content = ast.literal_eval(text_data)
		action = content['action']
		
		if action == 'placeship':
			game_id = content['game_id']
			start_row = content['start_row']
			start_col = content['start_col']
			ship_id = content['ship_id']
			game = Game.get_game(game_id)
			ship = Shipyard.get_ship(ship_id)
			vertical = (content['vertical'] == 'true') #note bool passed as string due to bug in literal_eval#begins checking if the given coordinates are legal
			#checks game hasn't started
			if not Game.get_both_ready(game_id):
				ship_count = User_Shipyard.get_user_shipyard_size(self.scope['user'], game_id)
				#checks that player hasn't already placed all their ships
				if ship_count < game.max_ships:
					if True:
						#checks if the ship sticks out off an edge
						safe = True
						if vertical:
							safe = start_row + ship.length <= game.num_rows
						else:
							safe = start_col + ship.length <= game.num_cols
						#checks that the ship won't overlap a previously placed one
						if safe:
							for i in range(0,ship.length):
								x = i
								y = 0
								if vertical:
									x = 0
									y = i
								if Cell.get_cell(game_id, self.scope['user'], 1, start_row+y, start_col+x).state != 'sea':
									safe = False
						#places the ship if it is safe to do so
						if safe:
							yard = User_Shipyard.add_user_ship(self.scope['user'].id,ship_id,game_id)
							for i in range(0,ship.length):
								x = i
								y = 0
								if vertical: 
									x = 0
									y = i
								Cell.set_cell_state(game_id, self.scope['user'], 1, start_row+y, start_col+x, '{0}'.format(yard.id))
							Game.set_ship_count(game_id,self.scope['user'],ship_count+1)
							

		if action == 'confirm':
			game_id = content['game_id']
			game = Game.get_game(game_id)
			for i in range(0,game.num_cols):
				for j in range(0,game.num_rows):
					#sets the ship to confirm its location
					cell = Cell.get_cell(game_id, self.scope['user'], 1, j, i)
					if cell.state != 'sea':
						cell.set = True;
						cell.save()
		
		if action == 'remove_ship':
			game_id = content['game_id']
			ship_id = content['ship_id']
			game = Game.get_game(game_id)
			yard_id = 0
			for i in range(0,game.num_cols):
				for j in range(0,game.num_rows):
					cell = Cell.get_cell(game_id, self.scope['user'], 1, j, i)
					if cell.state != 'sea' and not cell.set:
						yard_id = int(cell.state)
						Cell.set_cell_state(game_id, self.scope['user'], 1, j, i, 'sea')
			User_Shipyard.delete_user_ship(yard_id)
		
		if action == 'get_cells': #edited to return dictionary containing all cell states for the requested user dictform [side][x][y] = state
			message = {}
			game = Game.get_game(content['game_id'])
			for board_num in [1,2]:
				#does the following for each board the user has
				message[str(board_num-1)] = {}
				for x in range (0, game.num_cols):
					message[str(board_num-1)][str(x)] = {}
					for y in range(0, game.num_rows):
						#sets the message to conatain the cell state at every coordinate on the board
						cell_state = Cell.get_cell(content['game_id'], self.scope['user'], board_num, y, x).state
						message[str((board_num-1))][str(x)][str(y)] = cell_state
			messagefinal = {'cells' : message}
			self.send(text_data=json.dumps(messagefinal))
		
		if action == 'ready_to_start':
			game = Game.get_game(content['game_id'])
			#most code only tirggered in a bot game
			#if not bot game then only sets the player to ready, otherwise:
			if game.bot_game:
				ship_count = 0
				ship_array = [5]*game.ships_of_size_5 + [4]*game.ships_of_size_4 + [3]*game.ships_of_size_3 + [2]*game.ships_of_size_2 + [1]*game.ships_of_size_1
				#stops when all ships placed
				while ship_count < game.max_ships:
					#takes a set number of attempts to place a ship
					placed = False
					attempts = 0
					while not placed:
						ship = Shipyard.get_ship_by_length(ship_array[ship_count])
						#if it cant place the ship in the given number of attempts then it
						#wipes the board and starts again
						if attempts > 100:
							ship_count = 0
							placed = False
							User_Shipyard.delete_all_user_ships(game.p2)
							for r in range (0,game.num_rows):
								for c in range (0,game.num_cols):
									Cell.set_cell_state(content['game_id'],game.p2,1,r,c,'sea')
						#randomly selects coordinates and orientation of ship
						vertical = (random.randint(0,1) == 1)
						if vertical:
							start_row = random.randint(0,game.num_rows-ship.length)
							start_col = random.randint(0,game.num_cols-1)
							#checks that the ship won't lie over another
							safe = True
							for j in range(0,ship.length):
								if Cell.get_cell(content['game_id'],game.p2,1,start_row+j,start_col).state != 'sea':
									safe = False
							#places the ship if it is safe to do so
							if safe:
								yard = User_Shipyard.add_user_ship(game.p2.id,ship.id,game.id)
								ship_count+=1
								placed = True
								for j in range(0,ship.length):
									Cell.set_cell_state(content['game_id'],game.p2,1,start_row+j,start_col,'{0}'.format(yard.id))
						else:
							start_row = random.randint(0,game.num_rows-1)
							start_col = random.randint(0,game.num_cols-ship.length)
							#checks that the ship won't lie over another
							safe = True
							for j in range(0,ship.length):
								if Cell.get_cell(content['game_id'],game.p2,1,start_row,start_col+j).state != 'sea':
									safe = False
							#places the ship if it is safe to do so
							if safe:
								yard = User_Shipyard.add_user_ship(game.p2.id,ship.id,game.id)
								ship_count+=1
								placed = True
								for j in range(0,ship.length):
									Cell.set_cell_state(content['game_id'],game.p2,1,start_row,start_col+j,'{0}'.format(yard.id))
						attempts+=1
				#sets the bot as ready to play
				Game.set_ready(content['game_id'],game.p2.id)
				Game.set_ship_count(content['game_id'],game.p2,ship_count)
			#this part runs regardless of if its a bot game
			Game.set_ready(content['game_id'], self.scope['user'].id)
			self.send(text_data=json.dumps({'instruction': 'update'}))
			
		if action == 'get_turn':
			self.send(text_data=json.dumps({'player_turn': '{0}'.format(Game.get_game(content['game_id']).player_turn)}))
		
		if action == 'get_player_num':
			self.send(text_data=json.dumps({'player_num': '{0}'.format(Game.get_player_num(content['game_id'],self.scope['user']))}))
		
		if action == 'get_last_fired':
			self.send(text_data=json.dumps({'last_fired': Game.get_game(content['game_id']).last_fired}))
		
		if action == 'get_winner':
			self.send(text_data=json.dumps({'winner_num': Game.get_game(content['game_id']).winner}))
		
		if action == 'fire':
			game_id = content['game_id']
			row = content['row']
			col = content['col']
			game = Game.get_game(game_id)
			opponent = game.p1
			opponent_ship_count = game.p1_ship_count
			player_num = Game.get_player_num(game_id,self.scope['user'])
			#will only allow a shot if the game has started
			if Game.get_both_ready:
				if player_num == 1:
					opponent = game.p2
					opponent_ship_count = game.p2_ship_count
				#will only allow a shot if no one has won yet
				if (player_num != 0) and  (game.winner == 0):
					fired = False #bug fix for models not updating fast enough
					if game.player_turn == player_num:
						player_cell = Cell.get_cell(game_id, self.scope['user'], 2, row, col)
						opponent_cell = Cell.get_cell(game_id, opponent, 1, row, col)
						#will only allow a shot if the coordinates have not been previously fired at
						if player_cell.state == 'unknown':
							opponent_cell_state = opponent_cell.state
							#updates both players relevant boards depending on the state of the fired coordinates
							if opponent_cell_state == 'sea':
								Cell.set_cell_state(game_id, self.scope['user'], 2, row, col, 'miss')
								Game.set_last_fired(game_id,col,row,'miss')
								Cell.set_cell_state(game_id, opponent, 1, row, col, opponent_cell_state+'-fired_at')
							else:
								Cell.set_cell_state(game_id, self.scope['user'], 2, row, col, 'hit')
								Game.set_last_fired(game_id,col,row,'hit')
								Cell.set_cell_state(game_id, opponent, 1, row, col, opponent_cell_state+'-fired_at')
								yard_id = int(opponent_cell_state)
								#as a hit has been made it has to record the hit on the ship
								User_Shipyard.inc_hit_count(yard_id)
								ship_length = User_Shipyard.objects.get(id=yard_id).ship.length
								#checks if it sunk the ship
								if ship_length == User_Shipyard.get_ship(yard_id).hit_count:
									#if it has sunk the ship, then it updates the board with the sunk ship
									Game.set_ship_count(game_id, opponent, opponent_ship_count-1)
									Cell.sink_ship(game_id, yard_id, self.scope['user'], opponent)
									#checks to see if the user has won
									if opponent_ship_count == 1:
										Battleships_User.inc_games_played(self.scope['user'])
										Battleships_User.inc_games_played(opponent_id)
										Battleships_User.inc_wins(self.scope['user'])
										Game.set_winner(game_id,player_num)
							Game.set_next_turn(game_id, player_num)
							fired = True
				game = Game.get_game(game_id)
				#bot will fire back if it is a bot game
				if game.bot_game and (game.winner == 0):
					message = {}
					for board_num in [1,2]:
						message[str(board_num-1)] = {}
						for x in range (0, game.num_cols):
							message[str(board_num-1)][str(x)] = {}
							for y in range(0, game.num_rows):
								cell_state = Cell.get_cell(game_id, self.scope['user'], board_num, y, x).state
								message[str((board_num-1))][str(x)][str(y)] = cell_state
					messagefinal = {'cells' : message}
					self.send(text_data=json.dumps(messagefinal))
					self.send(text_data=json.dumps({'instruction': 'update'}))
					if fired:
						#updates its move list to see if it sunk a ship on its previous turn
						Bot_Moves.update_sunk(game_id)
						row = 0
						col = 0
						#if it has previously made a hit which has not led to a sunk ship then
						#it tries to find the rest of the ship
						#otherwise it guesses a location
						if Bot_Moves.check_for_outcome(game_id,'hit'):
							hits = Bot_Moves.get_moves(game_id,'hit')
							target = hits[random.randint(0,len(hits)-1)]
							row = target.y
							col = target.x
							#decides in the order to look to sink the ship as quickly as it can
							checking_direction = ((0,1),(0,-1),(1,0),(-1,0))
							if (Bot_Moves.check_fired_on(game_id,row+1,col) == 'hit') or (Bot_Moves.check_fired_on(game_id,row-1,col) == 'hit'):
								checking_direction = ((0,1),(0,-1),(1,0),(-1,0))
							elif (Bot_Moves.check_fired_on(game_id,row,col+1) == 'hit') or (Bot_Moves.check_fired_on(game_id,row,col-1) == 'hit'):
								checking_direction = ((1,0),(-1,0),(0,1),(0,-1))
							x = 0
							y = 0
							dir_num = 0
							cfo = 'hit'
							#finds the next place where the ship must be, or has its best guess
							while not (cfo == 'not_fired_on'):
								if (row+y >= game.num_rows) or (col+x >= game.num_cols) or (row+y < 0) or (col+x < 0):
									x = 0
									y = 0
									dir_num+=1
								cfo = Bot_Moves.check_fired_on(game_id,row+y,col+x)
								if cfo == 'hit':
									#can keep cheking in this direction
									x+=checking_direction[dir_num][0]
									y+=checking_direction[dir_num][1]
								elif (cfo == 'miss') or (cfo == 'sunk'):
									#needs to change direction
									x = 0
									y = 0
									dir_num+=1
								else:
									#potential position found
									row+=y
									col+=x
						else:
							attempts=0
							prefered=False
							row = random.randint(0,game.num_rows-1)
							col = random.randint(0,game.num_cols-1)
							#takes a set number of attempts to guess a place with at least a given 
							#number of unknown cells surrounding it, this way the guesses are more likely to hit
							while (attempts < 15) and not prefered:
								count = 0
								while Bot_Moves.check_fired_on(game_id,row,col) != 'not_fired_on':
									row = random.randint(0,game.num_rows-1)
									col = random.randint(0,game.num_cols-1)
								for i in range(row-1,row+2):
									for j in range(col-1,col+2):
										if Bot_Moves.check_fired_on(game_id,i,j) == 'not_fired_on':
											count+=1
								prefered=(count > 5) and (Bot_Moves.check_fired_on(game_id,row,col) == 'not_fired_on')
								attempts+=1
							#either it has found a prefered place or it hasn't, either way it has found a move it can make
						opponent_cell = Cell.get_cell(game_id,game.p1,1,row,col)
						opponent_cell_state = opponent_cell.state
						#depending on the state of the targeted cell, it updates both players boards accordingly
						if opponent_cell_state == 'sea':
							Cell.set_cell_state(game_id, game.p2, 2, row, col, 'miss')
							Game.set_last_fired(game_id,col,row,'miss')
							Cell.set_cell_state(game_id, game.p1, 1, row, col, opponent_cell_state+'-fired_at')
							Bot_Moves.add_move(game_id,row,col,'miss')
						else:
							Cell.set_cell_state(game_id, game.p2, 2, row, col, 'hit')
							Game.set_last_fired(game_id,col,row,'hit')
							Cell.set_cell_state(game_id, game.p1, 1, row, col, opponent_cell_state+'-fired_at')
							Bot_Moves.add_move(game_id,row,col,'hit')
							yard_id = int(opponent_cell_state)
							#as a hit has been made it has to record the hit on the ship
							User_Shipyard.inc_hit_count(yard_id)
							ship_length = User_Shipyard.objects.get(id=yard_id).ship.length
							#checks if it sunk the ship
							if ship_length == User_Shipyard.get_ship(yard_id).hit_count:
								#if it has sunk the ship, then it updates the board with the sunk ship
								Game.set_ship_count(game_id, game.p1, game.p1_ship_count-1)
								Cell.sink_ship(game_id, yard_id, game.p2, game.p1)
								#checks to see if it has won
								if game.p1_ship_count == 1:
									Game.set_winner(game_id,2)
						Game.set_next_turn(game_id, 2)	
						
		if action == 'update':
			game_id = content['game_id']
			game = Game.get_game(game_id)
			async_to_sync(self.channel_layer.group_send)('user-' + str(game.p1.id),{'type': 'update'})
			async_to_sync(self.channel_layer.group_send)('user-' + str(game.p2.id),{'type': 'update'})
						
	def update(self, event):
		self.send(text_data=json.dumps({'instruction': 'update'}))
		
	def disconnect(self, message, **kwargs):
		pass
