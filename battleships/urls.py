# battleships/urls.py
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('game.urls')),
    #url(r'^admin/', admin.site.urls),
]