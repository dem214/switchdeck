from rest_framework import serializers

from ..models import Dialog, Message

class DialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialog
        fields = ['uuid', 'participant1', 'participant2']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('uuid', 'dialog', 'sender', 'text', 'datetime')