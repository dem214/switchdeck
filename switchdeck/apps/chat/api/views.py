from rest_framework import viewsets, permissions, mixins

from .serializers import Dialog, DialogSerializer

class DialogViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):

    serializer_class = DialogSerializer
    queryset = Dialog.objects.all()

    def get_queryset(self):
        return Dialog.objects\
            .filter_by_user(self.request.user)\
            .select_related('participant1', 'participant2')

            

