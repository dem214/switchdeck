"""All forms of app `switchdeck`."""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, GameList, User, Profile, Game, Place


class CommentForm(forms.ModelForm):
    """Form for comments on `Gamelist` page."""

    class Meta():
        """Metaclass for `CommentForm` class properties."""

        model = Comment
        fields = ['text']


class GameListForm(forms.ModelForm):
    """Form to create new `GameListFrom`."""

    class Meta():
        """Metaclass for `GameListForm` class properties."""

        model = GameList
        fields = ['game', 'desc', 'prop', 'price']


class GameListReducedForm(forms.ModelForm):
    """
    Reduced form for create `Gamelist`.

    Not include `prop` and `price`
    """

    class Meta():
        """Metaclass for `GameListReducedForm` class properties."""

        model = GameList
        fields = ['game', 'desc']


class SetGameListForm(forms.ModelForm):
    """Form of `Gamelist` to set parameters."""

    class Meta():
        """Metaclass for `SetGameListForm` class properties."""

        model = GameList
        fields = ['desc', 'price']


class SignUpForm(UserCreationForm):
    """Form to signing up (creating new user profile)."""

    class Meta:
        """Metaclass for `SignUpForm` class properties."""

        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ChangeDescGamelistForm(forms.ModelForm):
    """Form to change description of `GameList`."""

    class Meta():
        """Metaclass for `ChangeDescGamelistForm` class properties."""

        model = GameList
        fields = ['desc']


class ChangePriceGamelistForm(forms.ModelForm):
    """Form to change price of `Gamelist`."""

    class Meta():
        """Metaclass for `ChangePriceGamelistForm` class properties."""

        model = GameList
        fields = ['price']


class UpdateProfileForm(forms.ModelForm):
    """Form to update user's profile page."""

    first_name = forms.CharField(max_length=30, strip=True, required=False)
    last_name = forms.CharField(max_length=150, strip=True, required=False)

    class Meta():
        """Metaclass for `UpdateProfile` class properties."""

        model = Profile
        fields = ['place']


class ChangeToForm(forms.Form):
    """Form contained by available variants of changable `Gamelists`."""

    changelets = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, instance, **kwargs):
        """Create form and add available variants."""
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
    """Widget with dropdown menu of available games."""

    def __init__(self, datalist, name, *args, **kwargs):
        """Initiate widget and fill it with data."""
        super().__init__(*args, **kwargs)
        self._name = name
        self._datalist = datalist
        self.attrs.update({'list': 'list_%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        """Return rendered html text of widget."""
        text_html = super().render(name, value, attrs=attrs)
        datalist = f'<datalist id="list_{self._name}">'
        for item in self._datalist:
            datalist += f'<option value="{item}">'
        datalist += '</datalist>'
        return (text_html + datalist)


class SearchForm(forms.Form):
    """Form from search of `Gamelists` page."""

    game = forms.CharField(required=False)
    place = forms.CharField(required=False)
    proposition = forms.ChoiceField(choices=(
        ('b', 'buy'),
        ('s', 'sell'),
        ('a', 'all')
    ))

    def __init__(self, *args, **kwargs):
        """Initiate form, fill it with needed widgets."""
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
