from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from .models import Comment, GameList, User, Profile

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

class ChangeToForm(forms.ModelForm):
    class Meta():
        model = GameList
        fields = ['change_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['change_to'].queryset = kwargs['instance'].get_change_to_choices()
