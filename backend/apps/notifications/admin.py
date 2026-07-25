from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'village',
        'publish_date',
        'is_pinned',
        'is_important',
        'status',
    )
    list_filter = (
        'category',
        'status',
        'is_important',
    )
    search_fields = (
        'title',
        'description',
    )
    ordering = ('-publish_date',)
    date_hierarchy = 'publish_date'
    list_editable = ('status', 'is_pinned', 'is_important')
