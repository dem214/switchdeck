from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, User

class SignUpForm(UserCreationForm):
    """Form to signing up (creating new user profile)."""

    class Meta:
        """Metaclass for `SignUpForm` class properties."""

        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UpdateProfileForm(forms.ModelForm):
    """Form to update user's profile page."""

    first_name = forms.CharField(max_length=30, strip=True, required=False)
    last_name = forms.CharField(max_length=150, strip=True, required=False)

    class Meta():
        """Metaclass for `UpdateProfile` class properties."""

        model = Profile
        fields = ['place']