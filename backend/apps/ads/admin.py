from django.contrib import admin
from .models import Ad


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'ad_type', 'expire_date', 'price', 'phone', 'status', 'created_at')
    list_filter = ('ad_type', 'status', 'expire_date', 'created_at')
    search_fields = ('title', 'description', 'phone', 'comment')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
