from django.urls import path
from .views import (
    ThreadCreateView, UserThreadsListView, MessageCreateView, MessageListView,
    MarkMessageAsReadView, UnreadMessagesCountView
)

urlpatterns = [
    path('threads/', ThreadCreateView.as_view(), name='thread-create'),
    path('threads/list/', UserThreadsListView.as_view(), name='user-threads'),
    path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    path('messages/list/<int:thread_id>/', MessageListView.as_view(), name='message-list'),
    path('messages/read/<int:pk>/', MarkMessageAsReadView.as_view(), name='message-read'),
    path('messages/unread-count/', UnreadMessagesCountView.as_view(), name='unread-messages'),
]