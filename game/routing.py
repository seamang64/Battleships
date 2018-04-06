from django.conf.urls import url

<<<<<<< HEAD
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/lobby/$', consumers.LobbyConsumer),
    url(r'^ws/game/(?P<game_id>\d+)/$', consumers.GameConsumer),
=======
from game.consumers import LobbyConsumer, GameConsumer

websocket_urlpatterns = [
    url(r'^ws/lobby/$', LobbyConsumer),
    url(r'^ws/game/(?P<game_id>\d+)/$', GameConsumer),
>>>>>>> pr/31
]