from django.conf.urls import url

from game.consumers import LobbyConsumer, GameConsumer

websocket_urlpatterns = [
    url(r'^ws/lobby/$', LobbyConsumer),
    url(r'^ws/game/(?P<game_id>\d+)/$', GameConsumer),
]