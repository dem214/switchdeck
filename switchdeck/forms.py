from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from .models import Comment, GameList, User, Profile, Game, Place

class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ['text']

class GameListForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['game', 'desc', 'prop', 'price']

class GameListReducedForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['game', 'desc']

class SetGameListForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['desc', 'price']

class SignUpForm(UserCreationForm):
    #email = forms.EmailField(max_length=200, help_text='Requiered')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ChangeDescGamelistForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['desc']

class ChangePriceGamelistForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['price']

class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, strip=True, required=False)
    last_name = forms.CharField(max_length=150, strip=True, required=False)
    class Meta():
        model = Profile
        fields = ['place']


class ChangeToForm(forms.Form):
    changelets = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        if instance.prop == 'w' or instance.prop == 'b':
            self.fields['changelets'].queryset = \
                instance.get_change_to_choices()
            self.fields['changelets'].initial = instance.change_to.all()
        elif instance.prop == 'k' or instance.prop == 's':
            self.fields['changelets'].queryset = \
                instance.get_ready_to_change_choices()
            self.fields['changelets'].initial = instance.ready_change_to.all()


class DatalistWidget(forms.TextInput):
    def __init__(self, datalist, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._datalist = datalist
        self.attrs.update({'list':'list_%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super().render(name, value, attrs=attrs)
        datalist = f'<datalist id="list_{self._name}">'
        for item in self._datalist:
            datalist += f'<option value="{item}">'
        datalist += '</datalist>'
        return (text_html + datalist)

class SearchForm(forms.Form):
    game = forms.CharField(required=False)
    place = forms.CharField(required=False)
    proposition = forms.ChoiceField(choices=(
        ('b', 'buy'),
        ('s', 'sell'),
        ('a', 'all')
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        list_game = [game.name for game in Game.objects.all()]
        list_game.sort()
        self.fields['game'].widget = DatalistWidget(
            datalist=list_game,
            name='game'
        )
        self.fields['place'].widget = DatalistWidget(
            datalist=[place.name for place in Place.objects.all()],
            name='place'
        )
