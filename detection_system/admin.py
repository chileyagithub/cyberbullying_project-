# Register your models here.

from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_toxic', 'created_at')
    list_filter = ('is_toxic',)
    search_fields = ('text',)

admin.site.register(Message, MessageAdmin)


