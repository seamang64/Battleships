# battleships/urls.py
from django.conf.urls import url, include
from django.contrib import admin
from game.views import __init__, api_views, views
from django.contrib.auth.views import login, logout
from rest_framework.routers import DefaultRouter


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.CreateUserView.as_view()),
    url(r'^login/$', login, {'template_name': 'login.html'}),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^lobby/$', views.LobbyView.as_view()),
    url(r'^$', views.HomeView.as_view()),
	url(r'^game/(?P<game_id>\d+)/$', views.GameView.as_view()),
	url(r'creategame/$', views.CreateGameView.as_view()),
]

urlpatterns += [
 url(r'^current-user/', api_views.CurrentUserView.as_view()),
 url(r'^game-from-id/(?P<game_id>\d+)/$', api_views.SingleGameViewSet.as_view()),
]

router = DefaultRouter()
router.register(r'player-games', api_views.PlayerGameViewSet, 'player_games')
router.register(r'available-games', api_views.AvailableGameViewSet, 'available_games')

urlpatterns += router.urls
