from django.contrib.auth.models import User
from .models import Game, Cell
from rest_framework import serializers
 
 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'groups')
 
 
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'p1', 'p2', 'num_cols', 
                  'num_rows', 'player_turn', 'p1_ship_count', 'p2_ship_count')
        depth = 1