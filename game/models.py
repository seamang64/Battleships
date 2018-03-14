from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
#from django-channels import Group
import json
from datetime import datetime

class Game(models.Model): #models game information not including the board
	winner = models.IntegerField(default=0) #0 for no one, 1 for player 1, 2 for player 2
	p1 = models.ForeignKey(User, related_name='p1') #player 1 identification, set to game creator
	p2 = models.ForeignKey(User, related_name='p2', null=True, blank=True) #player 2 identification, initially null
	num_cols = models.IntegerField(default=10) #number of rows of one players side of the board, size can be chosen but initially 8
	num_rows = models.IntegerField(default=10) #same for columns
	player_turn = models.IntegerField(default=1) #1 if player one's turn, 2 if player 2's
	p1_ship_count = models.IntegerField(default=10)
	p2_ship_count = models.IntegerField(default=10)
	
	
	def get_available_games(): #returns all games which don't yet have a second player
		return Game.objects.filter(p2=None)

	def create_new_game(user, cols, rows): #creates a new game, can specify the size of the board
		new_game = Game(p1=user, player_turn=1, num_cols=cols, num_rows=rows)
		new_game.save() #adds the game to the Game model
		return new_game
	
	def get_game(current_game): #returns the game which has the matching current game's id
		return Game.objects.get(pk=current_game)
	
	def set_next_turn(current_game): #alternates whose turn it is to play when called
		Game.objects.get(pk=current_game).update(player_num=3-F('player_turn'))
	
	def set_winner(current_game, player_num): #sets the winner field of a game to player 1 or 2
		Game.objects.get(pk=current_game).update(winner=player_num)
	
	def set_ship_count(current_game, player_id, new_count):
		game = Game.objects.get(pk=current_game)
		if player_id == game.p1:
			game.update(p1_ship_count=new_count)
		if player_id == game.p2:
			game.update(p2_ship_count=new_count)
	
	
class Cell(models.Model): #models every cell in every game
	game = models.ForeignKey(Game) #links each cell to a game
	x = models.IntegerField(default=0) #x-coordinate of cell
	y = models.IntegerField(default=0) #y-coordinate of cell
	state = models.CharField(max_length=20, default='sea') #eg: 'sea', 'hit', 'miss'
	user_owner = models.ForeignKey(User) 
	
	def get_cell_state(current_game, row, col, user): #returns the state of a cell
		return Cell.objects.get(game=current_game, x=col, y=row, user_owner=user).state
	
	def set_cell_state(current_game, row, col, player_num, new_state): #sets the state of a cell
		Cell.objects.get(game=current_game, x=col, y=row, user_owner=user).update(state=new_state)
	
	def create_new_board(game_id, rows, cols, p1_id, p2_id):
		for player_id in [p1_id, p2_id]:
			for r in range(0, rows):
				for c in range(0, cols):
					new_square = Cell(game=game_id, x=c, y=r, state='sea', user_owner=player_id)
					new_square.save() #for each player's side of the board it adds a cell to the Cell model
	

class Shipyard(models.Model):
	length = models.IntegerField(default=3)
	name = models.CharField(max_length=20, default='Submarine')
	
	def add_new_ship(ship_length,ship_name):
		Shipyard(length=ship_length, name=ship_name).save()
		
	def delete_ship_by_id(ship_id):
		Shipyard.objects.get(pk=ship_id).delete()
		
	def delete_ships_by_length(ship_length):
		Shipyard.objects.filter(length=ship_length).delete()
	
	def get_all_ships():
		return Shipyard.objects

class User(models.Model):
	username = models.CharField(max_length=30)
	
	def create_new_user(name):
		User(username=name).save()
	
	def delete_user(user_id):
		User.objects.get(pk=user_id).delete()
		
	def get_user(user_id):
		return User.objects.get(pk=user_id)

class User_Shipyard(models.Model):
	user = models.ForeignKey(User)
	ship = models.ForeignKey(Shipyard)
	
	def add_user_ship(user_id,ship_id):
		User_Shipyard(user_id,ship_id).save()
		
	def delete_user_ship(user_id,ship_id):
		User_Shipyard.objects.get(user_id,ship_id).delete()
		
	def get_user_shipyard_size(user_id):
		return User_Shipyard.objects.filter(user=user_id).count()
