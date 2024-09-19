from rest_framework import serializers
from .models import Thread, Message
from django.contrib.auth.models import User


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'participants', 'created', 'updated']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'text', 'created', 'is_read']
        read_only_fields = ['id', 'sender', 'created', 'is_read']

class UnreadMessagesCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()