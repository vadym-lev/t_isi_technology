from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, UnreadMessagesCountSerializer
from .permissions import IsAdminOrThreadParticipant, IsThreadParticipant

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

        if self.request.user not in serializer.validated_data['participants']:
            raise PermissionDenied("You must be a member of the thread.")

        thread = serializer.save()
        thread.participants.add(*participants)

        return Response(ThreadSerializer(thread).data, status=status.HTTP_201_CREATED)

# List threads for a user
class UserThreadsListView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)


class ThreadDeleteView(generics.DestroyAPIView):
    queryset = Thread.objects.all()
    # Admin or thread members can delete a thread
    permission_classes = [IsAuthenticated, IsAdminOrThreadParticipant]

    def get_object(self):
        thread_id = self.kwargs['thread_id']
        thread = Thread.objects.get(id=thread_id)
        self.check_object_permissions(self.request, thread)
        return thread

    def delete(self, request, *args, **kwargs):
        thread = self.get_object()
        self.perform_destroy(thread)
        return Response({"detail": "Thread deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Message creation and list
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsThreadParticipant]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thread = serializer.validated_data['thread']
        self.check_object_permissions(self.request, thread)
        message = serializer.save(sender=self.request.user)

        return Response(
            {"detail": "Message sent successfully", "message_id": message.id},
            status=status.HTTP_201_CREATED
        )

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    # Admin or thread members can get the thread
    permission_classes = [IsAuthenticated, IsAdminOrThreadParticipant]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        thread = Thread.objects.get(id=thread_id)
        # Checking the participant through permissions
        self.check_object_permissions(self.request, thread)
        return Message.objects.filter(thread=thread)

# Mark message as read
class MarkMessageAsReadView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        thread = message.thread
        # Check if the user is a member and not a sender
        self.check_object_permissions(request, thread)
        if request.user == message.sender:
            raise PermissionDenied("You cannot mark your own message as read.")
        message.is_read = True
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)


# Unread messages count
class UnreadMessagesCountView(generics.ListAPIView):
    serializer_class = UnreadMessagesCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # count the number of unread messages where the user is the recipient
        unread_count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return Response({'unread_count': unread_count})

