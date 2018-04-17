from rest_framework.views import APIView
from rest_framework import viewsets
from game.serializers import *
from rest_framework.response import Response
from game.models import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
 
class CurrentUserView(APIView):
 
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
 
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
 
 
class PlayerGameViewSet(viewsets.ViewSet):
    """
    API endpoint for player games
    """
 
    def list(self, request):
        queryset = Game.get_games_for_player(self.request.user)
        serializer = GameSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)
		
class AvailableGameViewSet(viewsets.ViewSet):
    """
    API endpoint for available/open games
    """
 
    def list(self, request):
        queryset = Game.get_available_games()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

class SingleGameViewSet(APIView):
	"""
	Get all data for a game: Game Details, cells and shipyard
	"""

	def get(self, request, **kwargs):
		game = Game.get_game(kwargs['game_id'])
		#cells = Cell.objects.filter(game==kwargs['game_id'])
		#shipyard = Shipyard.objects.all()
		shipyard = []
		for i in range(0, game.ships_of_size_1):
			shipyard.append(Shipyard.objects.get(length=1))
		for i in range(0, game.ships_of_size_2):
			shipyard.append(Shipyard.objects.get(length=2))
		for i in range(0, game.ships_of_size_3):
			shipyard.append(Shipyard.objects.get(length=3))
		for i in range(0, game.ships_of_size_4):
			shipyard.append(Shipyard.objects.get(length=4))
		for i in range(0, game.ships_of_size_5):
			shipyard.append(Shipyard.objects.get(length=5))
		game_serializer = GameSerializer(game)
		#cell_serializer = CellSerializer(cells, many=True)
		shipyard_serializer = ShipyardSerializer(shipyard, many=True)
		return_data = {'game': game_serializer.data,
                       'shipyard': shipyard_serializer.data}
		return Response(return_data)		

"""		
class CellViewSet(viewsets.ViewSet):
	def list(self, request):
		queryset = Cell.objects.filter(game==kwargs['game_id'])
		serializer = CellSerializer(queryset, many=True)
		return Response(serializer.data)
"""