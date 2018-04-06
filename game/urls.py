# game/urls.py
from django.conf.urls import url
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.CreateUserView.as_view()),
    url(r'^login/$', login, {'template_name': 'login.html'}),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^lobby/$', views.LobbyView.as_view()),
<<<<<<< HEAD
    url(r'^$', views.HomeView.as_view())
=======
    url(r'^$', views.HomeView.as_view()),
	url(r'^game/(?P<game_id>\d+)/$', GameView.as_view()),
>>>>>>> pr/31
]

urlpatterns += [
 url(r'^current-user/', api_views.CurrentUserView.as_view()),
<<<<<<< HEAD
]
router = DefaultRouter()
router.register(r'player-games', api_views.PlayerGameViewSet, 'player_games')
router.register(r'available-games', api_views.PlayerGameViewSet, 'available_games')
=======
 url(r'^game-from-id/(?P<game_id>\d+)/$', api_views.SingleGameViewSet.as_view()),
]
router = DefaultRouter()
router.register(r'player-games', api_views.PlayerGameViewSet, 'player_games')
router.register(r'available-games', api_views.AvailableGameViewSet, 'available_games')

>>>>>>> pr/31

urlpatterns += router.urls