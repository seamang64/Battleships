from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/lobby/$', consumers.LobbyConsumer),
    url(r'^ws/game/(?P<game_id>\d+)/$', consumers.GameConsumer),
]