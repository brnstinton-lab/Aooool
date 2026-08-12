from django.contrib.auth.models import AbstractUser
from django.db import models


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
