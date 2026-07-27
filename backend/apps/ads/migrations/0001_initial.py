# Generated migration for ads (Ad)
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('ad_type', models.CharField(
                    choices=[
                        ('SELL', 'Продам'),
                        ('BUY', 'Куплю'),
                        ('GIVE', 'Отдам'),
                        ('EXCHANGE', 'Обменяю'),
                        ('SEARCH', 'Ищу')
                    ],
                    max_length=20,
                    verbose_name='Тип объявления'
                )),
                ('category', models.CharField(
                    choices=[
                        ('FOOD', 'Продукты'),
                        ('ANIMALS', 'Животные'),
                        ('EQUIPMENT', 'Техника'),
                        ('BUILDING', 'Стройматериалы'),
                        ('CLOTHING', 'Одежда'),
                        ('ELECTRONICS', 'Электроника'),
                        ('OTHER', 'Разное')
                    ],
                    max_length=30,
                    verbose_name='Категория'
                )),
                ('description', models.TextField(verbose_name='Описание')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('price', models.PositiveIntegerField(blank=True, null=True, verbose_name='Цена (₸)')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('status', models.CharField(
                    choices=[
                        ('ACTIVE', 'Активное'),
                        ('ARCHIVED', 'В архиве')
                    ],
                    default='ACTIVE',
                    max_length=20,
                    verbose_name='Статус'
                )),
            ],
            options={
                'db_table': 'ads_ad',
                'verbose_name': 'Объявление',
                'verbose_name_plural': 'Объявления',
                'ordering': ['-created_at'],
            },
        ),
    ]
