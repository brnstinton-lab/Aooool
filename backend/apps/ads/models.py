from datetime import timedelta
from django.db import models
from django.utils import timezone


class AdQuerySet(models.QuerySet):
    def active(self):
        """Возвращает только активные объявления (со статусом ACTIVE и не старше 30 дней)"""
        cutoff = timezone.now() - timedelta(days=Ad.EXPIRATION_DAYS)
        return self.filter(
            status=self.model.Status.ACTIVE,
            created_at__gte=cutoff
        )


class AdManager(models.Manager):
    def get_queryset(self):
        return AdQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Ad(models.Model):
    """Модель объявления"""

    EXPIRATION_DAYS = 30

    class AdType(models.TextChoices):
        SELL = 'SELL', 'Продам'
        BUY = 'BUY', 'Куплю'
        GIVE = 'GIVE', 'Отдам'
        EXCHANGE = 'EXCHANGE', 'Обменяю'
        SEARCH = 'SEARCH', 'Ищу'

    class Category(models.TextChoices):
        FOOD = 'FOOD', 'Продукты'
        ANIMALS = 'ANIMALS', 'Животные'
        EQUIPMENT = 'EQUIPMENT', 'Техника'
        BUILDING = 'BUILDING', 'Стройматериалы'
        CLOTHING = 'CLOTHING', 'Одежда'
        ELECTRONICS = 'ELECTRONICS', 'Электроника'
        OTHER = 'OTHER', 'Разное'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активное'
        ARCHIVED = 'ARCHIVED', 'В архиве'

    # Обязательные поля
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    ad_type = models.CharField(
        max_length=20,
        choices=AdType.choices,
        verbose_name="Тип объявления"
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        verbose_name="Категория"
    )
    description = models.TextField(verbose_name="Описание")
    phone = models.CharField(max_length=30, verbose_name="Телефон")

    # Необязательные поля
    price = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Цена (₸)"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    # Служебные поля
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус"
    )

    objects = AdManager()

    class Meta:
        db_table = 'ads_ad'
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_ad_type_display()}] {self.title}"

    def is_expired(self) -> bool:
        """Проверяет, истекли ли 30 дней с момента публикации объявления"""
        if not self.created_at:
            return False
        expiration_date = self.created_at + timedelta(days=self.EXPIRATION_DAYS)
        return timezone.now() >= expiration_date

    def archive_if_expired(self) -> bool:
        """Переводит объявление в статус ARCHIVED, если его срок действия истек"""
        if self.status == self.Status.ACTIVE and self.is_expired():
            self.status = self.Status.ARCHIVED
            self.save(update_fields=['status'])
            return True
        return False
