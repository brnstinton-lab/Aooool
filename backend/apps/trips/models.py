from django.db import models
from django.utils import timezone
from django.conf import settings


class TripQuerySet(models.QuerySet):
    def upcoming(self):
        """Фильтрует только актуальные непросроченные поездки со статусом ACTIVE"""
        now = timezone.localtime(timezone.now())
        today = now.date()
        current_time = now.time()
        return self.filter(
            status=self.model.Status.ACTIVE
        ).filter(
            models.Q(trip_date__gt=today) |
            models.Q(trip_date=today, departure_time__isnull=True) |
            models.Q(trip_date=today, departure_time__gte=current_time)
        )


class TripManager(models.Manager):
    def get_queryset(self):
        return TripQuerySet(self.model, using=self._db)

    def upcoming(self):
        return self.get_queryset().upcoming()


class Trip(models.Model):
    """Модель поездки / попутчика"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активная'
        ARCHIVED = 'ARCHIVED', 'В архиве'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='trips',
        verbose_name="Автор"
    )

    driver_name = models.CharField(max_length=100, verbose_name="Имя водителя")
    phone = models.CharField(max_length=30, verbose_name="Телефон")
    from_location = models.CharField(max_length=100, verbose_name="Откуда")
    to_location = models.CharField(max_length=100, verbose_name="Куда")
    trip_date = models.DateField(verbose_name="Дата поездки")
    departure_time = models.TimeField(
        verbose_name="Время отправления", null=True, blank=True
    )
    seats_available = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Количество свободных мест"
    )
    price = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Стоимость (₸)"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )

    objects = TripManager()

    class Meta:
        verbose_name = "Поездка"
        verbose_name_plural = "Поездки"
        ordering = ["-trip_date", "-created_at"]

    def __str__(self):
        return f"{self.from_location} → {self.to_location} ({self.driver_name})"
