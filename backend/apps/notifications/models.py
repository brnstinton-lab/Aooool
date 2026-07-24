from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    class Category(models.TextChoices):
        ELECTRICITY = 'ELECTRICITY', '⚡ Электричество'
        WATER = 'WATER', '💧 Водоснабжение'
        ROADS = 'ROADS', '🚧 Дороги'
        EMERGENCY = 'EMERGENCY', '🚨 Экстренное'
        IMPORTANT = 'IMPORTANT', '📢 Важное'
        EVENT = 'EVENT', '🎉 Событие'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активно'
        ARCHIVED = 'ARCHIVED', 'В архиве'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.IMPORTANT,
        verbose_name="Категория"
    )
    village = models.CharField(
        max_length=100,
        default="с. Кабанбай",
        verbose_name="Населённый пункт"
    )
    publish_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата публикации"
    )
    expire_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания действия"
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name="Важное"
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name="Закреплено"
    )
    image = models.ImageField(
        upload_to="announcements/",
        null=True,
        blank=True,
        verbose_name="Изображение"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Официальное объявление"
        verbose_name_plural = "Официальные объявления"
        ordering = ["-is_pinned", "-publish_date"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
