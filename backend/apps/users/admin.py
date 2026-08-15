from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, Role, RoleRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Роль и телефон', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Роль и телефон', {'fields': ('role', 'phone')}),
    )


@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'requested_role',
        'master_specialization',
        'master_phone',
        'organization_name',
        'organization_category',
        'organization_phone',
        'status',
        'created_at',
        'reviewed_by',
        'reviewed_at'
    )
    list_filter = ('requested_role', 'status', 'organization_category', 'created_at')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'master_specialization', 'master_phone', 'master_description',
        'organization_name', 'organization_phone', 'organization_address', 'comment'
    )
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'requested_role', 'status', 'comment')
        }),
        ('Данные мастера (если применимо)', {
            'fields': (
                'master_specialization',
                'master_experience',
                'master_phone',
                'master_description',
            ),
        }),
        ('Данные организации (если применимо)', {
            'fields': (
                'organization_name',
                'organization_category',
                'organization_phone',
                'organization_address',
                'organization_description',
                'organization_working_hours',
            ),
        }),
        ('Информация об обработке', {
            'fields': ('created_at', 'reviewed_by', 'reviewed_at')
        }),
    )

    actions = ['approve_requests', 'reject_requests']

    def save_model(self, request, obj, form, change):
        if obj.status == RoleRequest.Status.APPROVED:
            obj.approve(reviewed_by=request.user)
        elif obj.status == RoleRequest.Status.REJECTED:
            obj.reject(reviewed_by=request.user)
        else:
            super().save_model(request, obj, form, change)

    @admin.action(description="Одобрить выбранные заявки")
    def approve_requests(self, request, queryset):
        count = 0
        for role_req in queryset:
            role_req.approve(reviewed_by=request.user)
            count += 1
        self.message_user(request, f"Одобрено заявок: {count}.")

    @admin.action(description="Отклонить выбранные заявки")
    def reject_requests(self, request, queryset):
        count = 0
        for role_req in queryset:
            role_req.reject(reviewed_by=request.user)
            count += 1
        self.message_user(request, f"Отклонено заявок: {count}.")
