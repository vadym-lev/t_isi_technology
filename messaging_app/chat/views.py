from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer
from django.contrib.auth.models import User

# Thread creation
class ThreadCreateView(generics.CreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        participants = self.request.data.get('participants')

        if len(participants) == 2:
            user1, user2 = participants
            existing_thread = Thread.objects.filter(participants=user1).filter(participants=user2).distinct()
            if existing_thread.exists():
                return Response(ThreadSerializer(existing_thread.first()).data)
        else:
            raise ValueError('Thread must have exactly 2 participants.')

        thread = serializer.save()
        thread.participants.add(*participants)

        return Response(ThreadSerializer(thread).data, status=status.HTTP_201_CREATED)

# List threads for a user
class UserThreadsListView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

# Message creation and list
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        return Message.objects.filter(thread__id=thread_id)

# Mark message as read
class MarkMessageAsReadView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(id=self.kwargs.get('pk'))

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.is_read = True
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)

# Unread messages count
class UnreadMessagesCountView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Message.objects.filter(thread__participants=request.user, is_read=False).count()
        return Response({'unread_count': unread_count})
