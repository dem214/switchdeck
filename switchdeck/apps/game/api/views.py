from rest_framework import viewsets, permissions

from .serializers import GameSerializer
from ..models import Game


class GameViewSet(viewsets.ModelViewSet):
    """List of api views for ``Game`` model."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        # IsStuffOrReadOnly
    ]