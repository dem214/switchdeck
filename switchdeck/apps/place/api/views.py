from rest_framework.viewsets import ModelViewSet

from ..models import Place
from .serializers import PlaceSerializer

class PlaceViewSet(ModelViewSet):
    """List of api views for ``Place`` model."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    # TODO maybe rewrite permissions
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
    #                       IsStuffOrReadOnly]