from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Place`` model."""
    class Meta:
        model = models.Place
        fields = ['url', 'id', 'name', 'popularity']


class GameSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Game`` model."""
    class Meta:
        model = models.Game
        fields = ['url', 'id', 'name', 'cover', 'description', 'eshop_url']


class GameListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``GameList`` model."""
    class Meta:
        model = models.GameList
        fields = ['url', 'id', 'profile', 'game', 'active', 'desc', 'prop',
                  'price', 'public_date', 'up_time', 'change_to', 'comments']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Comment`` model."""
    class Meta:
        model = models.Comment
        fields = ['url', 'id', 'author', 'timestamp', 'text', 'game_instance']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Profile`` model."""
    class Meta:
        model = models.Profile
        fields = ['url', 'id', 'user', 'place', 'gamelist_set']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``User`` model."""
    class Meta:
        model = get_user_model()
        fields = ['url', 'id', 'username']
