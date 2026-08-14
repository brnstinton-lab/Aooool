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
        'status',
        'created_at',
        'reviewed_by',
        'reviewed_at'
    )
    list_filter = ('requested_role', 'status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'comment')
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by')
    fields = (
        'user',
        'requested_role',
        'status',
        'comment',
        'created_at',
        'reviewed_by',
        'reviewed_at',
    )
    actions = ['approve_requests', 'reject_requests']

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = RoleRequest.objects.get(pk=obj.pk)
            if old_obj.status != obj.status and obj.status in [RoleRequest.Status.APPROVED, RoleRequest.Status.REJECTED]:
                obj.reviewed_at = timezone.now()
                obj.reviewed_by = request.user
                if obj.status == RoleRequest.Status.APPROVED:
                    if obj.requested_role in [RoleRequest.RequestedRole.MASTER, RoleRequest.RequestedRole.ORGANIZATION]:
                        obj.user.role = obj.requested_role
                        obj.user.save(update_fields=['role'])
            elif obj.status in [RoleRequest.Status.APPROVED, RoleRequest.Status.REJECTED] and not obj.reviewed_at:
                obj.reviewed_at = timezone.now()
                obj.reviewed_by = request.user
        else:
            if obj.status in [RoleRequest.Status.APPROVED, RoleRequest.Status.REJECTED]:
                obj.reviewed_at = timezone.now()
                obj.reviewed_by = request.user
                if obj.status == RoleRequest.Status.APPROVED:
                    if obj.requested_role in [RoleRequest.RequestedRole.MASTER, RoleRequest.RequestedRole.ORGANIZATION]:
                        obj.user.role = obj.requested_role
                        obj.user.save(update_fields=['role'])

        super().save_model(request, obj, form, change)

    @admin.action(description="Одобрить выбранные заявки")
    def approve_requests(self, request, queryset):
        count = 0
        now = timezone.now()
        for role_req in queryset:
            role_req.status = RoleRequest.Status.APPROVED
            role_req.reviewed_at = now
            role_req.reviewed_by = request.user
            role_req.save()
            if role_req.requested_role in [RoleRequest.RequestedRole.MASTER, RoleRequest.RequestedRole.ORGANIZATION]:
                role_req.user.role = role_req.requested_role
                role_req.user.save(update_fields=['role'])
            count += 1
        self.message_user(request, f"Одобрено заявок: {count}.")

    @admin.action(description="Отклонить выбранные заявки")
    def reject_requests(self, request, queryset):
        count = 0
        now = timezone.now()
        for role_req in queryset:
            role_req.status = RoleRequest.Status.REJECTED
            role_req.reviewed_at = now
            role_req.reviewed_by = request.user
            role_req.save()
            count += 1
        self.message_user(request, f"Отклонено заявок: {count}.")
