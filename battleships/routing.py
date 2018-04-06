from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
<<<<<<< HEAD
import game.routing
=======
from game import routing

from django.conf.urls import url

>>>>>>> pr/31

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
<<<<<<< HEAD
            game.routing.websocket_urlpatterns
=======
            routing.websocket_urlpatterns
>>>>>>> pr/31
        )
    ),
})