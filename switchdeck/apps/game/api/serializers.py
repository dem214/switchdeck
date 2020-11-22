from rest_framework import serializers

from ..models import Game


class GameSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Game`` model."""

    class Meta:
        """Metaclass for `GameSerializer` class with additional info."""

        model = Game
        fields = ['url', 'id', 'name', 'cover', 'description', 'eshop_url']