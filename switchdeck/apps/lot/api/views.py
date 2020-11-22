"""All views related to REST api of app."""
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

from . import serializers
from .. import models


class IsStuffOrReadOnly(permissions.BasePermission):
    """Permission checker - readonly for anonymous, processing for staff."""

    def has_object_permission(self, request, view, obj):
        """
        Check HTTP method and user permissions.

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
        Check HTTP method and user permissions.

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


class LotViewSet(viewsets.ModelViewSet):
    """List of api views for ``Lot`` model."""

    queryset = models.Lot.objects.all()
    serializer_class = serializers.LotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerProfileOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    """List of api views for ``Comment`` model."""

    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerAuthorOrReadOnly]
