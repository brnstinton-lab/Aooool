from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Role(models.TextChoices):
    RESIDENT = "resident", "Житель"
    MASTER = "master", "Мастер"
    ORGANIZATION = "organization", "Организация"
    ADMIN = "admin", "Администратор"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
        verbose_name="Роль"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Номер телефона"
    )

    class Meta:
        db_table = 'users_user'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class RoleRequest(models.Model):

    class RequestedRole(models.TextChoices):
        MASTER = "master", "Мастер"
        ORGANIZATION = "organization", "Организация"

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрено"
        REJECTED = "rejected", "Отклонено"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="role_requests",
        verbose_name="Пользователь"
    )

    requested_role = models.CharField(
        max_length=20,
        choices=RequestedRole.choices,
        verbose_name="Запрашиваемая роль"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус"
    )

    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата рассмотрения"
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_role_requests",
        verbose_name="Рассмотрел"
    )

    class Meta:
        db_table = 'users_rolerequest'
        verbose_name = "Заявка на смену роли"
        verbose_name_plural = "Заявки на смену роли"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='pending'),
                name='unique_pending_role_request_per_user'
            )
        ]

    def clean(self):
        super().clean()
        if self.status == self.Status.PENDING and not self.pk:
            if RoleRequest.objects.filter(user=self.user, status=self.Status.PENDING).exists():
                raise ValidationError("У вас уже есть активная заявка на рассмотрении.")

    def approve(self, reviewed_by=None, admin_comment=None):
        from django.utils import timezone
        self.status = self.Status.APPROVED
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if admin_comment:
            self.admin_comment = admin_comment
        self.save()

        self.user.role = self.requested_role
        self.user.save(update_fields=['role'])

    def reject(self, reviewed_by=None, admin_comment=None):
        from django.utils import timezone
        self.status = self.Status.REJECTED
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if admin_comment:
            self.admin_comment = admin_comment
        self.save()

    def __str__(self):
        return f"Заявка #{self.id} от {self.user.get_full_name() or self.user.username} ({self.get_requested_role_display()}) - {self.get_status_display()}"

