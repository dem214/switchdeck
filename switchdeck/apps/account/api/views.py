from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

from ..models import Profile
from .serializers import ProfileSerializer, UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """List of api views for ``Profile`` model."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        # IsStuffOrReadOnly
    ]

# TODO DO we realy need user views?
class UserViewSet(viewsets.ModelViewSet):
    """List of api views for ``User`` model."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        # IsStuffOrReadOnly
    ]