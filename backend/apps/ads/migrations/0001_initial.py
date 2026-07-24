# Generated migration for notifications (Announcement)
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('category', models.CharField(choices=[('ELECTRICITY', '⚡ Электричество'), ('WATER', '💧 Водоснабжение'), ('ROADS', '🚧 Дороги'), ('EMERGENCY', '🚨 Экстренное'), ('IMPORTANT', '📢 Важное'), ('EVENT', '🎉 Событие')], default='IMPORTANT', max_length=20, verbose_name='Категория')),
                ('village', models.CharField(default='с. Кабанбай', max_length=100, verbose_name='Населённый пункт')),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('expire_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания действия')),
                ('is_important', models.BooleanField(default=False, verbose_name='Важное')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='Закреплено')),
                ('image', models.ImageField(blank=True, null=True, upload_to='announcements/', verbose_name='Изображение')),
                ('status', models.CharField(choices=[('ACTIVE', 'Активно'), ('ARCHIVED', 'В архиве')], default='ACTIVE', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Официальное объявление',
                'verbose_name_plural': 'Официальные объявления',
                'ordering': ['-is_pinned', '-publish_date'],
            },
        ),
    ]
