from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from django.contrib.auth.models import User
import json
from asgiref.sync import async_to_sync
from .models import Game, User, User_Shipyard, Battleships_User, Cell
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
			print(max)
			game = Game.create_new_game(player, content['height'], content['width'], max, content['shipyard'],False)
			User_Shipyard.delete_all_user_ships(player)
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
			print(max)
			game = Game.create_new_game(player, content['height'], content['width'], max, content['shipyard'],True)
			User_Shipyard.delete_all_user_ships(player)
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'new_game',
					'player': game.p1.username,
					'game': game.id
				}
			)
			i = 0
			while User.objects.filter(username='bot{0}'.format(i)).exists():
				i+=1
			user = User.objects.create_user('bot{0}'.format(i))
			add_p2(game.pk,user.pk)

		if action == 'delete_game':
			game = Game.get_game(content['game_id'])
			if game.bot_game:
				Bot_Moves.delete_game(content['game_id'])
			Game.delete_game(content['game_id'],self.message.user)

		if action == 'find_game':
			return Game.get_available_games()
		
		if action == 'create_board':
			Cell.create_new_board(content['game_id'], content['rows'], content['cols'], content['p1_id'], content['p2_id'])
			
		#if action == 'place_ship':
		#	Cell.set_cell_state(content['game_id'], content['rows'], content['cols'], content['player_id'], content['new_state'])
		
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
		
		#if action == 'add_user_ship':
		#	User_Shipyard.add_user_ship(content['user_id'], content['ship_id'])
		
		if action == 'get_user_shipyard_size':
			return get_user_shipyard_size(content['user_id'])
	
		#if action == 'delete_user_ship':
		#	User_Shipyard.delete_user_ship(content['user_id'], content['ship_id'])
			
	def new_game(self, event):
		avail_game_list = Game.get_available_games()
		avail_serializer = GameSerializer(avail_game_list, many=True)
		other_data = {'player': event['player'], 'game': event['game']}
		self.send(text_data=json.dumps(avail_serializer.data))
		self.send(text_data=json.dumps(other_data))
		

class GameConsumer(JsonWebsocketConsumer):
	
	http_user = True

	def connect(self, **kwargs):
		#self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'user-' + str(self.scope['user'].id)
		
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)
		
		self.accept()
		
		async_to_sync(self.channel_layer.group_send)('user-' + str(self.scope['user'].id),{'type': 'update'})

	def receive(self, text_data, **kwargs):
		"""
		Called when a message is received with either text or bytes
		filled out.
		"""
		channel_session_user = True
		content = ast.literal_eval(text_data)
		action = content['action']
		
		if action == 'placeship':
			print("Placing")
			game_id = content['game_id']
			start_row = content['start_row']
			start_col = content['start_col']
			ship_id = content['ship_id']
			game = Game.get_game(game_id)
			ship = Shipyard.get_ship(ship_id)
			if not Game.get_both_ready(game_id):
				ship_count = User_Shipyard.get_user_shipyard_size(self.scope['user'])
				if ship_count < game.max_ships:
					if not User_Shipyard.contains_user_ship(self.scope['user'],ship_id):
						safe = True
						if vertical:
							safe = start_row + ship.length < game.num_rows
						else:
							safe = start_col + ship.length < game.num_cols
						if safe:
							for i in range(0,ship.length):
								x = i
								y = 0
								if vertical:
									x = 0
									y = i
								if Cell.get_cell(game_id, self.message.user, 1, start_row+y, start_col+x) != 'sea':
									safe = False
						if safe:
							print("Ready")
							yard = User_Shipyard.add_user_ship(self.scope['user'].id,ship_id)
							print('yard')
							for i in range(0,ship.length):
								x = i
								y = 0
								if content['vertical'] == 'true': #note bool passed as string due to bug in literal_eval
									x = 0
									y = i
								Cell.set_cell_state(game_id, self.scope['user'], 1, start_row+y, start_col+x, '{0}'.format(yard.id))
							Game.set_ship_count(game_id,self.message.user,ship_count+1)

		if action == 'confirm':
			game_id = content['game_id']
			game = Game.get_game(game_id)
			for i in range(0,game.num_cols):
				for j in range(0,game.num_rows):
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
				message[str(board_num-1)] = {}
				for x in range (0, game.num_cols):
					message[str(board_num-1)][str(x)] = {}
					for y in range(0, game.num_rows):
						cell_state = Cell.get_cell(content['game_id'], self.scope['user'], board_num, y, x).state
						message[str((board_num-1))][str(x)][str(y)] = cell_state
			messagefinal = {'cells' : message}
			self.send(text_data=json.dumps(messagefinal))
		
		if action == 'ready_to_start':
			game = Game.get(content['game_id'])
			if game.bot_game:
				ship_count = 0
				while ship_count < game.max_ships:
					placed = False
					attempts = 0
					while not placed:
						if attempts > 200:
							ship_count = 0
							placed = False
							User_Shipyard.delete_all_user_ships(game.p2)
							for r in range (0,game.num_rows):
								for c in range (0,game.num_cols):
									Cell.set_cell_state(content['game_id'],game.p2,1,r,c,'sea')
						vertical = (random.randint(0,2) == 1)
						if vertical:
							size = random.randint(1,game.num_rows+1)
							while not Shipyard.has_ship_of_length(size):
								size = random.randint(1,game.num_rows+1)
							ship = Shipyard.get_ship_by_length(size)
							start_row = random.randint(0,game.num_rows-ship.length+1)
							start_col = random.randint(0,game.num_cols)
							safe = True
							for j in range(0,ship.length):
								if Cell.get_cell(content['game_id'],game.p2,1,start_row+j,start_col) != 'sea':
									safe = False
							if safe:
								yard = User_Shipyard.add_user_ship(game.p2,ship_id)
								ship_count+=1
								placed = True
								for j in range(0,ship.length):
									Cell.set_cell_state(content['game_id'],game.p2,1,start_row+j,start_col,'{0}'.format(yard.id))
						else:
							size = random.randint(1,game.num_cols+1)
							while not Shipyard.has_ship_of_length(size):
								size = random.randint(1,game.num_cols+1)
							ship = Shipyard.get_ship_by_length(size)
							start_row = random.randint(0,game.num_rows)
							start_col = random.randint(0,game.num_cols-ship.length+1)
							safe = True
							for j in range(0,ship.length):
								if Cell.get_cell(content['game_id'],game.p2,1,start_row,start_col+j) != 'sea':
									safe = False
							if safe:
								yard = User_Shipyard.add_user_ship(game.p2,ship_id)
								ship_count+=1
								placed = True
								for j in range(0,ship.length):
									Cell.set_cell_state(content['game_id'],game.p2,1,start_row,start_col+j,'{0}'.format(yard.id))
						attempts+=1
				Game.set_ready(content['game_id'],game.p2)
			Game.set_ready(content['game_id'], self.scope['user'].id)
		
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
			if Game.get_both_ready:
				if player_num == 1:
					opponent = game.p2
					opponent_ship_count = game.p2_ship_count
				if player_num != 0:
					if game.player_turn == player_num:
						player_cell = Cell.get_cell(game_id, self.scope['user'], 2, row, col)
						opponent_cell = Cell.get_cell(game_id, opponent, 1, row, col)
						if player_cell.state == 'unknown':
							opponent_cell_state = opponent_cell.state
							if opponent_cell_state == 'sea':
								Cell.set_cell_state(game_id, self.scope['user'], 2, row, col, 'miss')
								Game.set_last_fired(game_id,col,row,'miss')
								Cell.set_cell_state(game_id, opponent, 1, row, col, opponent_cell_state+'-fired_at')
								add_Move(game_id,row,col,'miss')
							else:
								Cell.set_cell_state(game_id, self.scope['user'], 2, row, col, 'hit')
								Game.set_last_fired(game_id,col,row,'hit')
								Cell.set_cell_state(game_id, opponent, 1, row, col, opponent_cell_state+'-fired_at')
								add_Move(game_id,row,col,'hit')
								yard_id = int(opponent_cell_state)
								User_Shipyard.inc_hit_count(yard_id)
								ship_length = User_Shipyard.objects.get(id=yard_id).ship.length
								if ship_length == User_Shipyard.get_ship(yard_id).hit_count:
									Game.set_ship_count(game_id, opponent, opponent_ship_count-1)
									Cell.sink_ship(game_id, yard_id, self.scope['user'], opponent)
									if opponent_ship_count == 1:
										#Battleships_User.inc_games_played(self.scope['user'])
										#Battleships_User.inc_games_played(opponent_id)
										#Battleships_User.inc_wins(self.scope['user'])
										Game.set_winner(game_id,player_num)
							Game.set_next_turn(game_id, player_num)
				if game.bot_game:
					if game.player_turn == 2:
						Bot_Moves.update_sunk(game_id)
						row = 0
						col = 0
						if Bot_Moves.check_for_outcome(game_id,'hit'):
							hits = Bot_Moves.get_moves(game_id,'hit')
							target = hits[random.randint(0,len(hits))]
							row = target.y
							col = target.x
							x = 0
							y = 0
							checking_direction = ((0,1),(0,-1),(1,0),(-1,0))
							dir_num = 0
							cfo = 'hit'
							while cfo == 'hit':
								if (row+y > game.num_rows) or (col+x > game.num_cols):
									x = 0
									y = 0
									dir_num+=1
								cfo = check_fired_on(game_id,row+y,col+x)
								if cfo == 'hit':
									x+=checking_direction[dir_num][0]
									y+=checking_direction[dir_num][1]
								elif (cfo == 'miss') or (cfo == 'sunk'):
									x = 0
									y = 0
									dir_num+=1
								else:
									row+=y
									col+=x
						else:
							row = random.randint(0,game.num_rows)
							col = random.randint(0,game.num_cols)
							while check_fired_on(game_id,row,col) != 'not_fired_on':
								row = random.randint(0,game.num_rows)
								col = random.randint(0,game.num_cols)
							opponent_cell = Cell.get_cell(game_id,game.p1,1,row,col)
							opponent_cell_state = opponent_cell.state
							if opponent_cell_state == 'sea':
								Cell.set_cell_state(game_id, game.p2, 2, row, col, 'miss')
								Game.set_last_fired(game_id,col,row,'miss')
								Cell.set_cell_state(game_id, game.p1, 1, row, col, opponent_cell_state+'-fired_at')
							else:
								Cell.set_cell_state(game_id, game.p2, 2, row, col, 'hit')
								Game.set_last_fired(game_id,col,row,'hit')
								Cell.set_cell_state(game_id, game.p1, 1, row, col, opponent_cell_state+'-fired_at')
								yard_id = int(opponent_cell_state)
								User_Shipyard.inc_hit_count(yard_id)
								ship_length = User_Shipyard.objects.get(id=yard_id).ship.length
								if ship_length == User_Shipyard.get_ship(yard_id).hit_count:
									Game.set_ship_count(game_id, game.p1, game.p1_ship_count-1)
									Cell.sink_ship(game_id, yard_id, game.p2, game.p1)
									if game.p1_ship_count == 1:
										Game.set_winner(game_id,2)			
						Game.set_next_turn(game_id, player_num)	
						
		if action == 'update':
			game_id = content['game_id']
			game = Game.get_game(game_id)
			async_to_sync(self.channel_layer.group_send)('user-' + str(game.p1.id),{'type': 'update'})
			async_to_sync(self.channel_layer.group_send)('user-' + str(game.p2.id),{'type': 'update'})
						
	def update(self, event):
		self.send(text_data=json.dumps({'instruction': 'update'}))
		
	def disconnect(self, message, **kwargs):
		"""
		Perform things on connection close
		"""
		pass
		
