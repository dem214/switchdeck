"""Serialization classes and method for REST api JSON."""
from rest_framework import serializers

from ..models import Lot, Comment


class LotSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Lot`` model."""

    class Meta:
        """Metaclass for `LotSerializer` class with additional info."""

        model = Lot
        fields = ['url', 'id', 'profile', 'game', 'active', 'desc', 'prop',
                  'price', 'public_date', 'up_time', 'change_to', 'comments']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Comment`` model."""

    class Meta:
        """Metaclass for `CommentSerializer` class with additional info."""

        model = Comment
        fields = ['url', 'id', 'author', 'timestamp', 'text', 'lot']

