from django.contrib import admin
from .models import Thread, Message

class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'updated']
    search_fields = ['id']

class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'text', 'created', 'is_read']
    search_fields = ['text', 'sender__username']

admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)