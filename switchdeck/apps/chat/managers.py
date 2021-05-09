from django.db import models
from django.db.models import Q

class DialogManager(models.Manager):

    def filter_by_user(self, user):
        return self.filter(Q(participant1=user) | Q(participant2=user))

    def filter_users_room(self, user1, user2):
        return self.filter(
            Q(participant1=user1, participant2=user2) 
            | Q(participant1=user2, participant2=user1)
        )

    def get_user_room(self, user1, user2):
        return self.filter_users_room(user1, user2).get()