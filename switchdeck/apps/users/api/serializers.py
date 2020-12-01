from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Profile, User

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Profile`` model."""

    class Meta:
        """Metaclass for `ProfileSerializer` class with additional info."""

        model = Profile
        fields = ['url', 'user', 'place', 'lot_set']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``User`` model."""

    class Meta:
        """Metaclass for `UserSerializer` class with additional info."""

        model = get_user_model()
        fields = ['url', 'username']