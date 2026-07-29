from django.db import models


class DirectoryEntry(models.Model):
    """Модель записи в справочнике аула"""

    class Category(models.TextChoices):
        EMERGENCY = 'emergency', 'Экстренные службы'
        UTILITIES = 'utilities', 'Коммунальные службы'
        MASTERS = 'masters', 'Мастера и специалисты'
        ORGANIZATIONS = 'organizations', 'Организации'
        SHOPS = 'shops', 'Магазины'
        PHARMACIES = 'pharmacies', 'Аптеки'
        SCHOOLS = 'schools', 'Школы и детсады'
        HOSPITALS = 'hospitals', 'Больницы и медучреждения'
        TAXI = 'taxi', 'Такси'
        CAFE = 'cafe', 'Кафе и еда'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        INACTIVE = 'inactive', 'Неактивно'

    name = models.CharField(max_length=255, verbose_name="Название")
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name="Категория"
    )
    phone = models.CharField(max_length=32, verbose_name="Телефон")
    second_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Дополнительный телефон"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Адрес"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )
    working_hours = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Режим работы"
    )
    priority = models.IntegerField(
        default=0,
        verbose_name="Приоритет"
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
        db_table = 'directory_entry'
        verbose_name = "Запись справочника"
        verbose_name_plural = "Справочник аула"
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
