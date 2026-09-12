from django.contrib import admin
from .models import Announcement, NotificationPreference, PushSubscription
from .push_service import send_push_notification


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'announcement_type',
        'category',
        'user',
        'village',
        'status',
        'is_important',
        'is_pinned',
        'publish_date',
        'has_image',
    )
    list_filter = (
        'announcement_type',
        'status',
        'category',
        'is_important',
        'is_pinned',
        'village',
    )
    search_fields = (
        'title',
        'description',
        'location',
        'child_name',
        'contact_phone',
        'user__username',
        'user__first_name',
        'user__last_name',
    )
    ordering = ('-publish_date',)
    date_hierarchy = 'publish_date'
    list_editable = ('status', 'is_pinned', 'is_important')
    actions = ['approve_announcements', 'archive_announcements', 'reject_announcements']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'announcement_type',
                'category',
                'title',
                'description',
                'user',
                'status',
                'village',
            )
        }),
        ('Срочное происшествие / Пропавший ребёнок', {
            'classes': ('collapse',),
            'fields': (
                'location',
                'incident_time',
                'contact_phone',
                'child_name',
                'child_age',
                'appearance',
                'clothing',
                'extra_info',
            )
        }),
        ('Медиа и параметры отображения', {
            'fields': (
                'image',
                'is_important',
                'is_pinned',
                'publish_date',
                'expire_date',
            )
        }),
    )

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Фото"

    @admin.action(description="✅ Одобрить и опубликовать (ACTIVE)")
    def approve_announcements(self, request, queryset):
        count = 0
        for item in queryset:
            item.status = Announcement.Status.ACTIVE
            item.save()
            try:
                send_push_notification(item)
            except Exception:
                pass
            count += 1
        self.message_user(request, f"Опубликовано объявлений: {count}")

    @admin.action(description="📦 Перенести в архив (ARCHIVED)")
    def archive_announcements(self, request, queryset):
        count = queryset.update(status=Announcement.Status.ARCHIVED)
        self.message_user(request, f"Перенесено в архив: {count}")

    @admin.action(description="❌ Отклонить (REJECTED)")
    def reject_announcements(self, request, queryset):
        count = queryset.update(status=Announcement.Status.REJECTED)
        self.message_user(request, f"Отклонено объявлений: {count}")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'urgent_enabled', 'official_enabled', 'updated_at')
    list_filter = ('urgent_enabled', 'official_enabled')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__phone')


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'endpoint')

