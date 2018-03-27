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
	p1_ready = models.BooleanField(default=False)
	p2_ready = models.BooleanField(default=False)

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

	def create_new_game(user, cols, rows, ships):
		new_game = Game(p1=user, num_cols=cols, num_rows=rows, player_turn=1, p1_ship_count=0, p2_ship_count=0, max_ships=ships, p1_ready=False, p2_ready=False)
		new_game.save()
		return new_game
	
	def add_p2(game_id,p2_id):
		Game.objects.filter(pk=game_id).update(p2=p2_id)
	
	def delete_game(game_id):
		Game.objects.filter(pk=game_id).delete()
	
	def get_player_num(game_id, player_id):
		game = Game.objects.get(pk=game_id)
		if player_id == game.p1:
			return 1
		elif player_id == game.p2:
			return 2
		else:
			return 0
	
	def set_next_turn(game_id):
		Game.objects.filter(pk=game_id).update(player_turn=3-F('player_turn'))
	
	def set_ship_count(game_id, player_id, new_count):
		game = Game.objects.filter(pk=game_id)
		if player_id == game.p1:
			game.update(p1_ship_count=new_count)
		if player_id == game.p2:
			game.update(p2_ship_count=new_count)
	
	def get_both_ready(game_id):
		game = Game.objects.filter(pk=game_id)
		return game.p1_ready and game.p2_ready
	
	def set_ready(game_id, player_id):
		game = Game.objects.filter(pk=game_id)
		if player_id == game.p1:
			game.update(p1_ready=true)
		if player_id == game.p2:
			game.update(p2_ready=true)

class Shipyard(models.Model):
	length = models.IntegerField(default=3)
	name = models.CharField(max_length=20)
	
	def get_all_ships():
		return Shipyard.objects
	
	def get_ship(ship_id):
		return Shipyard.objects.get(pk=ship_id)
	
	def add_new_ship(ship_length,ship_name):
		Shipyard(length=ship_length, name=ship_name).save()
		
	def delete_ship_by_id(ship_id):
		Shipyard.objects.filter(pk=ship_id).delete()
		
	def delete_ships_by_length(ship_length):
		Shipyard.objects.filter(length=ship_length).delete()

class User_Shipyard(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ship = models.ForeignKey(Shipyard, on_delete=models.CASCADE)
	hit_count = models.IntegerField(default=0)
	
	def get_all_user_ships(user_id):
		return User_Shipyard.objects.filter(user=user_id)
	
	def get_ship(user_id,ship_id):
		return User_Shipyard.objects.get(user=user_id, ship=ship_id)
	
	def contains_user_ship(user_id,ship_id):
		return (User_Shipyard.objects.filter(user=user_id,ship=ship_id) != [])
	
	def add_user_ship(user_id,ship_id):
		User_Shipyard(user_id,ship_id,0).save()
		
	def delete_all_user_ships(user_id):
		User_Shipyard.objects.filter(user=user_id).delete()
		
	def get_user_shipyard_size(user_id):
		return User_Shipyard.objects.filter(user=user_id).count()
	
	def inc_hit_count(user_id,ship_id):
		ship = User_Shipyard.objects.get(user=user_id, ship=ship_id)
		hc = ship.hit_count
		ship.update(hit_count=hc+1)
	
class Cell(models.Model): 
	game = models.ForeignKey(Game, on_delete=models.CASCADE) 
	user_owner = models.ForeignKey(User, on_delete=models.CASCADE)
	board_type = models.IntegerField(default=0)
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0) 
	state = models.CharField(max_length=20, default='sea') 
	
	def get_cell(game_id, user, board_num, row, col): 
		return Cell.objects.get(game=game_id, user_owner=user, board_type=board_num, x=col, y=row)
	
	def set_cell_state(game_id, user, board_num, row, col, new_state): 
		Cell.objects.filter(game=game_id, user_owner=user, board_type=board_num, x=col, y=row).update(state=new_state)
	
	def create_new_board(game_id, rows, cols, p1_id, p2_id):
		for player_id in [p1_id, p2_id]:
			for type in [1, 2]:
				if type == 1: cell_state = 'sea'
				else: cell_state = 'unknown'
				for r in range(0, rows):
					for c in range(0, cols):
						new_square = Cell(game=game_id, user_owner=player_id, board_type=type, x=c, y=r, state=cell_state)
						new_square.save() 

	def delete_game_boards(game_id):
		Cell.objects.filter(game=game_id).delete()

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
	
	