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

    # Поля для заявки мастера
    master_specialization = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Специализация мастера"
    )

    master_experience = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Опыт работы мастера"
    )

    master_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Телефон мастера"
    )

    master_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание услуг мастера"
    )

    # Поля для заявки организации
    organization_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название организации"
    )

    organization_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Категория организации"
    )

    organization_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Телефон организации"
    )

    organization_address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Адрес организации"
    )

    organization_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание организации"
    )

    organization_working_hours = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Режим работы"
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
        from apps.directory.models import DirectoryEntry

        self.status = self.Status.APPROVED
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.save()

        # 1. Назначаем пользователю роль
        self.user.role = self.requested_role
        self.user.save(update_fields=['role'])

        # 2. Если запрашиваемая роль — Организация, создаём запись в справочнике без дублирования
        if self.requested_role == self.RequestedRole.ORGANIZATION:
            org_name = self.organization_name
            if not org_name and self.comment:
                for line in self.comment.splitlines():
                    if line.startswith("Название:"):
                        org_name = line.replace("Название:", "").strip()
                        break
            if not org_name:
                org_name = self.user.get_full_name() or self.user.username

            org_category = self.organization_category or DirectoryEntry.Category.ORGANIZATIONS
            org_phone = self.organization_phone or getattr(self.user, 'phone', '') or ''
            org_address = self.organization_address or ''
            org_description = self.organization_description or ''
            org_working_hours = self.organization_working_hours or ''

            # Проверка от дублирования при повторном сохранении/одобрении
            DirectoryEntry.objects.get_or_create(
                name=org_name,
                phone=org_phone,
                defaults={
                    'category': org_category,
                    'address': org_address,
                    'description': org_description,
                    'working_hours': org_working_hours,
                    'status': DirectoryEntry.Status.ACTIVE
                }
            )

        # 3. Если запрашиваемая роль — Мастер, создаём запись в справочнике без дублирования
        elif self.requested_role == self.RequestedRole.MASTER:
            master_name = self.user.get_full_name() or self.user.username
            master_phone = self.master_phone or getattr(self.user, 'phone', '') or ''

            spec = self.master_specialization or ''
            exp = self.master_experience or ''
            desc = self.master_description or ''

            # Совместимость со старыми заявками, где поля были только в comment
            if not spec and self.comment:
                for line in self.comment.splitlines():
                    if line.startswith("Специализация:"):
                        spec = line.replace("Специализация:", "").strip()
                    elif line.startswith("Опыт работы:"):
                        exp = line.replace("Опыт работы:", "").strip()
                    elif line.startswith("Телефон:") and not master_phone:
                        master_phone = line.replace("Телефон:", "").strip()
                    elif line.startswith("Описание:"):
                        desc = line.replace("Описание:", "").strip()

            description_parts = []
            if spec:
                description_parts.append(spec)
            if exp:
                description_parts.append(f"Опыт: {exp}")
            if desc:
                description_parts.append(desc)

            full_description = "\n".join(description_parts) if description_parts else (self.comment or '')

            DirectoryEntry.objects.get_or_create(
                name=master_name,
                phone=master_phone,
                defaults={
                    'category': DirectoryEntry.Category.MASTERS,
                    'description': full_description,
                    'status': DirectoryEntry.Status.ACTIVE
                }
            )

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

