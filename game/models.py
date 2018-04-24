from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import json

class Game(models.Model): 
	p1 = models.ForeignKey(User, related_name='p1', on_delete=models.CASCADE) 
	p2 = models.ForeignKey(User, related_name='p2', null=True, blank=True, on_delete=models.CASCADE) 
	num_cols = models.IntegerField(default=10)
	num_rows = models.IntegerField(default=10)
	player_turn = models.IntegerField(default=1) 
	p1_ship_count = models.IntegerField(default=0)
	p2_ship_count = models.IntegerField(default=0)
	max_ships = models.IntegerField(default=10)
	ships_of_size_1 = models.IntegerField(default=0)
	ships_of_size_2 = models.IntegerField(default=0)
	ships_of_size_3 = models.IntegerField(default=0)
	ships_of_size_4 = models.IntegerField(default=0)
	ships_of_size_5 = models.IntegerField(default=0)
	p1_ready = models.BooleanField(default=False)
	p2_ready = models.BooleanField(default=False)
	last_fired = models.CharField(default='( , )-hit_or_miss',max_length=15)
	winner = models.IntegerField(default=0)
	bot_game = models.BooleanField(default=False)

	def get_available_games():
		return Game.objects.filter(p2=None)
	
	@staticmethod
	def created_count(user_id):
		return Game.objects.filter(p1=user_id).count()
	
	@staticmethod
	def get_games_for_player(user_id):
		from django.db.models import Q
		return Game.objects.filter(Q(p1=user_id) | Q(p2=user_id))
	
	def get_game(game_id):
		return Game.objects.get(pk=game_id)

	def create_new_game(user, cols, rows, max, ships, bot):
		new_game = Game(p1=user, num_cols=cols, num_rows=rows, player_turn=1, p1_ship_count=max, p2_ship_count=max, max_ships=max, ships_of_size_1=ships[0], ships_of_size_2=ships[1], ships_of_size_3=ships[2], ships_of_size_4=ships[3], ships_of_size_5=ships[4], p1_ready=False, p2_ready=False, last_fired='( , )-hit_or_miss', winner=0, bot_game=bot)
		new_game.save()
		return new_game
	
	def add_p2(game_id,p2_id):		
		Game.objects.get(pk=game_id).p2=p2_id
		Game.objects.get(pk=game_id).save()
		
	def delete_game(game_id,creator_id):
		game = Game.get_game(game_id)
		if game.bot_game:
			User.objects.get(pk=game.p2).delete()
		Game.objects.get(pk=game_id,p1=creator_id).delete()
	
	def get_player_num(game_id, player_id):
		game = Game.objects.get(pk=game_id)
		if player_id == game.p1:
			return 1
		elif player_id == game.p2:
			return 2
		else:
			return 0
	
	def set_next_turn(game_id, player_num):
		game=Game.objects.get(pk=game_id)
		game.player_turn=3-player_num
		game.save()
	
	def set_ship_count(game_id, player_id, new_count):
		game = Game.objects.get(pk=game_id)
		if player_id == game.p1:
			game.p1_ship_count=new_count
		if player_id == game.p2:
			game.p2_ship_count=new_count
		game.save()
	
	def get_both_ready(game_id):
		game = Game.objects.get(pk=game_id)
		return game.p1_ready and game.p2_ready
	
	def set_ready(game_id, player_id):
		game = Game.objects.get(pk=game_id)
		if (player_id == game.p1.id):
			game.p1_ready=True
		if (player_id == game.p2.id):
			game.p2_ready=True
		game.save()
	
	def set_last_fired(game_id,x,y,hit_or_miss):
		Game.objects.get(pk=game_id).last_fired='({0},{0})-{0}'.format(x,y,hit_or_miss)
		Game.objects.get(pk=game_id).save()
	
	def set_winner(game_id,player_num):
		game=Game.objects.get(pk=game_id)
		game.winner=player_num
		game.save()

class Shipyard(models.Model):
	length = models.IntegerField(default=3)
	name = models.CharField(max_length=20)
	
	def get_all_ships():
		return Shipyard.objects.all()
	
	def get_ship(ship_id):
		return Shipyard.objects.get(pk=ship_id)
	
	def add_new_ship(ship_length,ship_name):
		Shipyard(length=ship_length, name=ship_name).save()
		
	def delete_ship_by_id(ship_id):
		Shipyard.objects.filter(pk=ship_id).delete()
		
	def delete_ships_by_length(ship_length):
		Shipyard.objects.filter(length=ship_length).delete()
	
	def get_ship_by_length(leng):
		return Shipyard.objects.get(length=leng)
	
	def has_ship_of_length(leng):
		return (Shipyard.objects.filter(length=leng).exists())


class User_Shipyard(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ship = models.ForeignKey(Shipyard, on_delete=models.CASCADE)
	hit_count = models.IntegerField(default=0)
	sunk = models.BooleanField(default=False)
	
	def get_all_user_ships(user_id):
		return User_Shipyard.objects.filter(user=user_id)
	
	def get_ship(yard_id):
		return User_Shipyard.objects.get(id=yard_id)
	
	def contains_user_ship(user_id,ship_id):
		return (User_Shipyard.objects.filter(user=user_id,ship=ship_id).exists())
	
	def add_user_ship(user_id,ship_id):
		yard = User_Shipyard(user=User.objects.get(pk=user_id),ship=Shipyard.get_ship(ship_id),hit_count=0)
		yard.save()
		return yard
	
	def delete_user_ship(yard_id):
		User_Shipyard.objects.filter(id=yard_id).delete()
		
	def delete_all_user_ships(user_id):
		User_Shipyard.objects.filter(user=user_id).delete()
		
	def get_user_shipyard_size(user_id):
		return User_Shipyard.objects.filter(user=user_id).count()
	
	def inc_hit_count(yard_id):
		ship = User_Shipyard.objects.get(id=yard_id)
		hc = ship.hit_count
		ship.hit_count=hc+1
		if ship.hit_count==Shipyard.get_ship(ship.ship.id).length:
			ship.sunk=True
		ship.save()

	
class Cell(models.Model): 
	game = models.ForeignKey(Game, on_delete=models.CASCADE) 
	user_owner = models.ForeignKey(User, on_delete=models.CASCADE)
	board_type = models.IntegerField(default=0)
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0) 
	state = models.CharField(max_length=20, default='sea')
	set = models.BooleanField(default=False)
	
	def get_cell(game_id, user, board_num, row, col): 
		return Cell.objects.get(game_id=game_id, user_owner=user, board_type=board_num, x=col, y=row)
	
	def set_cell_state(game_id, user, board_num, row, col, new_state): 
		Cell.objects.filter(game_id=game_id, user_owner=user, board_type=board_num, x=col, y=row).update(state=new_state)
	
	def create_new_board(game_id, rows, cols, p1, p2):
		for player in [p1, p2]:
			for type in [1, 2]:
				if type == 1: cell_state = 'sea'
				else: cell_state = 'unknown'
				for r in range(0, rows):
					for c in range(0, cols):
						new_square = Cell(game=Game.get_game(game_id), user_owner=player, board_type=type, x=c, y=r, state=cell_state)
						new_square.save() 

	def delete_game_boards(game_id):
		Cell.objects.filter(game=game_id).delete()
		
	def sink_ship(game_id, yard_id, player, opponent):
		game = Game.get_game(game_id)
		for x in range (0, game.num_cols):
			for y in range (0, game.num_rows):
				if (Cell.get_cell(game_id, opponent, 1, y, x).state == str(yard_id) +'-fired_at'):
					Cell.set_cell_state(game_id, opponent, 1, y, x, str(yard_id) + "-sunk")
					Cell.set_cell_state(game_id, player, 2, y, x, "sunk")

class Bot_Moves(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	outcome = models.CharField(max_length=20, default='miss')
	
	def add_Move(game_id,row,col,hit_or_miss):
		Bot_Moves(game=game_id,x=col,y=row,outcome=hit_or_miss).save()
	
	def check_fired_on(game_id,row,col):
		if (Bot_Moves.objects.filter(game=game_id,x=col,y=row).exists()):
			return Bot_Moves.objects.get(game=game_id,x=col,y=row).outcome
		else:
			return 'not_fired_on'
	
	def check_for_outcome(game_id,hit_miss_sunk):
		return (Bot_Moves.objects.filter(game=game_id,outcome=hit_miss_sunk).exists())
	
	def get_moves(game_id,hit_miss_sunk):
		return Bot_Moves.objects.filter(game=game_id,outcome=hit_miss_sunk)
		
	def update_sunk(game_id):
		b_game = Game.get_game(game_id)
		for col in range (0, game.num_cols):
			for row in range (0, game.num_rows):
				if (Cell.get_cell(game_id, b_game.p1, 2, row, col).state == 'sunk'):
					Bot_Moves.objects.get(game=game_id,x=col,y=row).update(outcome='sunk')
	
	def delete_game(game_id):
		Bot_Moves.objects.filter(game=game_id).delete()

class Battleships_User(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	wins = models.IntegerField(default=0)
	games_played = models.IntegerField(default=0)
	
	def add_user(user_id):
		Battleships_User(user=user_id, wins=0, games_played=0).save()
	
	def delete_user(user_id):
		Battleships_User.objects.get(user=user_id).delete()
	
	def get_user(user_id):
		return Battleships_User.objects.get(user=user_id)
	
	def inc_wins(user_id):
		Battleships_User.objects.get(user=user_id).update(wins=F('wins')+1)
	
	def inc_games_played(user_id):
		Battleships_User.objects.get(user=user_id).update(games_played=F('games_played')+1)
