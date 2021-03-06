from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.contrib import messages
from game.models import Game, Cell, Battleships_User

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        message = []
        for i in range(0, len(Battleships_User.objects.all())):
            message.append(Battleships_User.objects.all()[i])
        message.sort(key=lambda x: -x.wins)
        context['top_five'] = message[:5]
        current_user = self.request.user
        context['logged_in'] = True
        try:
            current_battle_user = Battleships_User.get_user(current_user.id)
            context['current'] = current_battle_user
            if current_battle_user.games_played != 0:
                context['current_wl'] = round(current_battle_user.wins / current_battle_user.games_played, 2)
            else:
                context['current_wl'] = "N/A"
        except:
            context['logged_in'] = False
        return context
 
class CreateUserView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = '/'
 
    def form_valid(self, form):
        valid = super(CreateUserView, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        battle_user = Battleships_User.add_user(new_user)
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
        player_games = Game.get_games_for_player(self.request.user)

        return context
		
class CreateGameView(TemplateView):
		template_name = 'components/lobby/create_game.html'

class GameView(TemplateView):
    template_name = 'components/game/game.html'
    game = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # get the game by the id
        self.game = Game.get_game(kwargs['game_id'])
        user = get_user(request)
        # check to see if the game is open and available for this user
        # if this player is the creator, just return
        if self.game.p1 == user or self.game.p2 == user:
            return super(GameView, self).dispatch(request, *args, **kwargs)
			
        # if there is no opponent and the game is not yet completed,
        # set the opponent as this user
        if not self.game.p2 and self.game.winner == 0:
            self.game.p2 = user
            Cell.create_new_board(self.game.id, self.game.num_rows, self.game.num_cols, self.game.p1, self.game.p2)
            self.game.save()
            return super(GameView, self).dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Sorry, the selected game is not available.')
            return redirect('/lobby/')
 
    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        context['game'] = self.game
 
        return context
