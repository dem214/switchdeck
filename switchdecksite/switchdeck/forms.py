from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from .models import Comment, GameList, User

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
