from django.db import models
from django.utils import timezone
from django.conf import settings


class Announcement(models.Model):
    class AnnouncementType(models.TextChoices):
        URGENT = 'URGENT', '🚨 Срочное происшествие'
        OFFICIAL = 'OFFICIAL', '📢 Официальное объявление'

    class Category(models.TextChoices):
        # Срочные происшествия
        MISSING_CHILD = 'MISSING_CHILD', '🚸 Пропал ребёнок'
        MISSING_PERSON = 'MISSING_PERSON', '🔍 Пропал человек'
        FIRE = 'FIRE', '🔥 Пожар / задымление'
        ACCIDENT = 'ACCIDENT', '💥 Авария / ДТП'
        DANGER = 'DANGER', '⚠️ Опасность для жителей'
        OTHER_URGENT = 'OTHER_URGENT', '🚨 Другое происшествие'

        # Официальные оповещения
        ELECTRICITY = 'ELECTRICITY', '⚡ Электричество'
        WATER = 'WATER', '💧 Водоснабжение'
        ROADS = 'ROADS', '🚧 Дороги'
        UTILITIES = 'UTILITIES', '🛠 Коммунальные работы'
        SCHEDULE = 'SCHEDULE', '🕒 Режим работы'
        EVENT = 'EVENT', '🎉 Событие'
        IMPORTANT = 'IMPORTANT', '📢 Важное'
        EMERGENCY = 'EMERGENCY', '🚨 Экстренное'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'На модерации'
        ACTIVE = 'ACTIVE', 'Активно'
        REJECTED = 'REJECTED', 'Отклонено'
        ARCHIVED = 'ARCHIVED', 'В архиве'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="Автор"
    )
    announcement_type = models.CharField(
        max_length=20,
        choices=AnnouncementType.choices,
        default=AnnouncementType.OFFICIAL,
        verbose_name="Тип оповещения"
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    category = models.CharField(
        max_length=30,
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
        verbose_name="Изображение / Фото"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус"
    )

    # Детализированные поля для срочных оповещений
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Место происшествия / Где видели"
    )
    incident_time = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Дата и время происшествия"
    )
    contact_phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Контактный телефон"
    )

    # Специфические поля для «Пропал ребёнок»
    child_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя и фамилия"
    )
    child_age = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Возраст"
    )
    appearance = models.TextField(
        blank=True,
        verbose_name="Внешность и приметы"
    )
    clothing = models.TextField(
        blank=True,
        verbose_name="Одежда"
    )
    extra_info = models.TextField(
        blank=True,
        verbose_name="Дополнительная информация"
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
        verbose_name = "Оповещение"
        verbose_name_plural = "Оповещения"
        ordering = ["-is_pinned", "-publish_date"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    @property
    def is_urgent(self):
        return self.announcement_type == self.AnnouncementType.URGENT

    @property
    def is_official(self):
        return self.announcement_type == self.AnnouncementType.OFFICIAL

