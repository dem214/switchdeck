from rest_framework.serializers import HyperlinkedModelSerializer

from ..models import Place


class PlaceSerializer(HyperlinkedModelSerializer):
    """Serializer/Desirializer of ``Place`` model."""

    class Meta:
        """Metaclass for `PlaceSerializer` class with additional info."""

        model = Place
        fields = ['url', 'name', 'popularity']