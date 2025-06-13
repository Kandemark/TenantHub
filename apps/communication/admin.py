from django.contrib import admin
from .models import Message, Thread, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'content', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'sender')
    search_fields = ('content', 'sender__username', 'thread__id')
    raw_id_fields = ('thread', 'sender')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    search_fields = ('id',)
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'recipient')
    search_fields = ('message', 'recipient__username')
    raw_id_fields = ('recipient',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

# Register your models here.
