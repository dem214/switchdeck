"""Serialization classes and method for REST api JSON."""
from rest_framework import serializers

from . import models


class GameSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Game`` model."""

    class Meta:
        """Metaclass for `GameSerializer` class with additional info."""

        model = models.Game
        fields = ['url', 'id', 'name', 'cover', 'description', 'eshop_url']


class LotSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Lot`` model."""

    class Meta:
        """Metaclass for `LotSerializer` class with additional info."""

        model = models.Lot
        fields = ['url', 'id', 'profile', 'game', 'active', 'desc', 'prop',
                  'price', 'public_date', 'up_time', 'change_to', 'comments']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Comment`` model."""

    class Meta:
        """Metaclass for `CommentSerializer` class with additional info."""

        model = models.Comment
        fields = ['url', 'id', 'author', 'timestamp', 'text', 'game_instance']

