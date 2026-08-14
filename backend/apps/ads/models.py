from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings


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

    # Автор объявления
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ads',
        verbose_name="Автор"
    )

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

    def get_relative_time(self) -> str:
        """Возвращает относительное время создания объявления (Только что, N минут назад, N часов назад)"""
        if not self.created_at:
            return "Только что"
        now = timezone.now()
        if self.created_at > now:
            return "Только что"
        diff = now - self.created_at
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "Только что"

        minutes = seconds // 60
        if minutes < 60:
            if minutes % 10 == 1 and minutes % 100 != 11:
                return f"{minutes} минуту назад"
            elif minutes % 10 in (2, 3, 4) and minutes % 100 not in (12, 13, 14):
                return f"{minutes} минуты назад"
            else:
                return f"{minutes} минут назад"

        hours = minutes // 60
        if hours < 24:
            if hours % 10 == 1 and hours % 100 != 11:
                return f"{hours} час назад"
            elif hours % 10 in (2, 3, 4) and hours % 100 not in (12, 13, 14):
                return f"{hours} часа назад"
            else:
                return f"{hours} часов назад"

        days = hours // 24
        if days == 1:
            return "Вчера"
        elif days < 7:
            if days % 10 in (2, 3, 4) and days % 100 not in (12, 13, 14):
                return f"{days} дня назад"
            else:
                return f"{days} дней назад"
        else:
            from django.utils.formats import date_format
            return date_format(timezone.localtime(self.created_at), "j E")

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


class AdImage(models.Model):
    """Модель фотографии объявления"""
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Объявление"
    )
    image = models.ImageField(
        upload_to='ads/photos/%Y/%m/',
        verbose_name="Фотография"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )

    class Meta:
        db_table = 'ads_ad_image'
        verbose_name = "Фотография объявления"
        verbose_name_plural = "Фотографии объявлений"
        ordering = ['id']

    def __str__(self):
        return f"Фото #{self.id} для объявления [{self.ad_id}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                from PIL import Image
                img_path = self.image.path
                img = Image.open(img_path)
                max_size = (1600, 1600)
                if img.height > max_size[1] or img.width > max_size[0]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
                    img.save(img_path, quality=85, optimize=True)
            except Exception:
                pass
