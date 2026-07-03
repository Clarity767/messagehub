from django.contrib import admin
from .models import Profile, Note, Message


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'user__email']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'done', 'created_at']
    list_filter = ['done', 'priority']
    search_fields = ['title', 'content']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['subject', 'body']