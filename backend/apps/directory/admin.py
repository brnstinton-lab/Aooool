from django.contrib import admin
from .models import DirectoryEntry


@admin.register(DirectoryEntry)
class DirectoryEntryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'phone',
        'second_phone',
        'priority',
        'status',
        'created_at',
    )
    list_filter = ('category', 'status')
    search_fields = ('name', 'phone', 'second_phone', 'address')
    ordering = ('-priority', 'name')
    list_editable = ('priority', 'status')
