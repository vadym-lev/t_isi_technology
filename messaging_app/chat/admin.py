from django.contrib import admin
from .models import Thread, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    readonly_fields = ('created', 'sender')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ('participants__username',)
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'text', 'is_read', 'created')
    list_filter = ('is_read', 'created')
    search_fields = ('sender__username', 'text')
    list_editable = ('is_read',)
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Mark selected messages as read'