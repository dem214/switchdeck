"""All views related to REST api of app."""
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

from . import serializer, models


class IsStuffOrReadOnly(permissions.BasePermission):
    """Permission checker - readonly for anonymous, processing for staff."""

    def has_object_permission(self, request, view, obj):
        """
        Check HTML method and user permissions.

        Return `True` if used safe methods of user is from staff.
        """
        print(dir(request.user))
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsOwnerProfileOrReadOnly(permissions.BasePermission):
    """
    Permission checker.

    Readonly for anonymous, processing for users in
    ``profile`` field.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check HTML method and user permissions.

        Return `True` if used safe methods of user on them profile page.
        """
        print(dir(request.user))
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.profile == request.user.profile


class IsOwnerAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission checker.

    Readonly for anonymous, processing for users in
    ``author`` field.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check HTML method and user permissions.

        Return `True` if used safe methods of user own this comment.
        """
        print(dir(request.user))
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user.profile


class GameViewSet(viewsets.ModelViewSet):
    """List of api views for ``Game`` model."""

    queryset = models.Game.objects.all()
    serializer_class = serializer.GameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsStuffOrReadOnly]


class LotViewSet(viewsets.ModelViewSet):
    """List of api views for ``Lot`` model."""

    queryset = models.Lot.objects.all()
    serializer_class = serializer.LotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerProfileOrReadOnly]


class ProfileViewSet(viewsets.ModelViewSet):
    """List of api views for ``Profile`` model."""

    queryset = models.Profile.objects.all()
    serializer_class = serializer.ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsStuffOrReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    """List of api views for ``User`` model."""

    queryset = get_user_model().objects.all()
    serializer_class = serializer.UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsStuffOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    """List of api views for ``Comment`` model."""

    queryset = models.Comment.objects.all()
    serializer_class = serializer.CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerAuthorOrReadOnly]
