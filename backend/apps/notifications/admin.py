from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'village',
        'is_important',
        'is_pinned',
        'status',
        'publish_date',
    )
    list_filter = (
        'category',
        'status',
        'village',
        'is_important',
        'is_pinned',
    )
    search_fields = (
        'title',
        'description',
        'village',
    )
    ordering = ('-publish_date',)
    date_hierarchy = 'publish_date'
