from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from game.models import Game

class HomeView(TemplateView):
    template_name = 'home.html'
 
 
class CreateUserView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = '/'
 
    def form_valid(self, form):
        valid = super(CreateUserView, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid

		
class LobbyView(TemplateView):
    template_name = 'components/lobby/lobby.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LobbyView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LobbyView, self).get_context_data(**kwargs)
        # get current open games to prepopulate the list

        # we're creating a list of games that contains just the id (for the link) and the creator
        available_games = [{'creator': game.p1.username, 'id': game.pk} for game in Game.get_available_games()]
        # for the player's games, we're returning a list of games with the opponent and id
        #player_games = Game.get_games_for_player(self.request.user)

        return context