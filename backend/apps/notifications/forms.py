from django import forms
from .models import Announcement


URGENT_CATEGORIES = [
    (Announcement.Category.MISSING_CHILD, '🚸 Пропал ребёнок'),
    (Announcement.Category.MISSING_PERSON, '🔍 Пропал человек'),
    (Announcement.Category.FIRE, '🔥 Пожар / задымление'),
    (Announcement.Category.ACCIDENT, '💥 Авария / ДТП'),
    (Announcement.Category.DANGER, '⚠️ Опасность для жителей'),
    (Announcement.Category.OTHER_URGENT, '🚨 Другое происшествие'),
]

OFFICIAL_CATEGORIES = [
    (Announcement.Category.ELECTRICITY, '⚡ Электричество'),
    (Announcement.Category.WATER, '💧 Водоснабжение'),
    (Announcement.Category.ROADS, '🚧 Дороги'),
    (Announcement.Category.UTILITIES, '🛠 Коммунальные работы'),
    (Announcement.Category.SCHEDULE, '🕒 Режим работы'),
    (Announcement.Category.EVENT, '🎉 Событие'),
    (Announcement.Category.IMPORTANT, '📢 Важное'),
    (Announcement.Category.EMERGENCY, '🚨 Экстренное'),
]


class UrgentNotificationForm(forms.ModelForm):
    """
    Форма создания срочного происшествия.
    Доступна любому авторизованному жителю/мастеру/организации.
    Публикуется сразу со статусом ACTIVE.
    """
    category = forms.ChoiceField(
        choices=URGENT_CATEGORIES,
        label="Категория происшествия",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
            'x-model': 'selectedCategory'
        })
    )
    title = forms.CharField(
        required=False,
        label="Краткий заголовок",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
            'placeholder': 'Например: Задымление на окраине села'
        })
    )
    description = forms.CharField(
        required=False,
        label="Подробное описание происшествия",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
            'rows': 3,
            'placeholder': 'Опишите что произошло, требуется ли помощь...'
        })
    )

    class Meta:
        model = Announcement
        fields = [
            'category',
            'title',
            'description',
            'location',
            'incident_time',
            'contact_phone',
            'image',
            # Поля для пропавшего ребенка
            'child_name',
            'child_age',
            'appearance',
            'clothing',
            'extra_info',
        ]
        labels = {
            'title': 'Краткий заголовок',
            'description': 'Подробное описание происшествия',
            'location': 'Место происшествия / Где видели',
            'incident_time': 'Дата и время происшествия',
            'contact_phone': 'Контактный телефон для связи',
            'image': 'Фотография',
            'child_name': 'Имя и фамилия ребёнка',
            'child_age': 'Возраст ребёнка',
            'appearance': 'Внешность и особые приметы (рост, волосы, глаза)',
            'clothing': 'Во что был(а) одет(а)',
            'extra_info': 'Дополнительная важная информация',
        }
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'placeholder': 'ул. Абая, возле магазина / восточная окраина'
            }),
            'incident_time': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'placeholder': 'Сегодня в 14:30 / 20 минут назад'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'placeholder': '+7 (7XX) XXX-XX-XX'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'urgent_photo_input',
                'accept': 'image/*',
                '@change': 'handleFileChange($event)'
            }),
            'child_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'placeholder': 'Имя и фамилия ребёнка'
            }),
            'child_age': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'placeholder': 'Например: 8 лет'
            }),
            'appearance': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'rows': 2,
                'placeholder': 'Рост 130 см, худенький, светлые волосы, родинка на щеке...'
            }),
            'clothing': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'rows': 2,
                'placeholder': 'Синяя куртка с капюшоном, черные джинсы, серые кроссовки...'
            }),
            'extra_info': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:bg-white transition text-sm',
                'rows': 2,
                'placeholder': 'Может отзываться на кличку, боится собак, был с велосипедом...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        image = cleaned_data.get('image')
        contact_phone = cleaned_data.get('contact_phone')
        title = cleaned_data.get('title')

        # Для «Пропал ребёнок» действуют строгие правила
        if category == Announcement.Category.MISSING_CHILD:
            if not image:
                self.add_error('image', 'Для категории «Пропал ребёнок» прикрепление фотографии обязательно!')
            
            child_name = cleaned_data.get('child_name', '').strip()
            child_age = cleaned_data.get('child_age', '').strip()
            location = cleaned_data.get('location', '').strip()

            if not child_name:
                self.add_error('child_name', 'Укажите имя и фамилию ребёнка.')
            if not child_age:
                self.add_error('child_age', 'Укажите возраст ребёнка.')
            if not location:
                self.add_error('location', 'Укажите место, где ребёнка видели в последний раз.')
            if not contact_phone:
                self.add_error('contact_phone', 'Укажите контактный телефон родителей или ответственных лиц.')

            # Авто-формирование понятного заголовка, если пользователь оставил пустым
            if not title and child_name:
                cleaned_data['title'] = f"Пропал ребёнок: {child_name} ({child_age})"

            # Если описание не заполнено, собираем его из структурированных полей
            description = cleaned_data.get('description', '').strip()
            if not description:
                desc_parts = [
                    f"Пропал ребёнок: {child_name}, возраст: {child_age}.",
                    f"Где видели: {location}.",
                ]
                if cleaned_data.get('incident_time'):
                    desc_parts.append(f"Время: {cleaned_data.get('incident_time')}.")
                if cleaned_data.get('clothing'):
                    desc_parts.append(f"Одежда: {cleaned_data.get('clothing')}.")
                if cleaned_data.get('appearance'):
                    desc_parts.append(f"Приметы: {cleaned_data.get('appearance')}.")
                if cleaned_data.get('extra_info'):
                    desc_parts.append(f"Дополнительно: {cleaned_data.get('extra_info')}.")
                cleaned_data['description'] = "\n".join(desc_parts)

        else:
            # Для других срочных категорий
            if not title:
                self.add_error('title', 'Укажите краткий заголовок происшествия.')
            if not cleaned_data.get('description'):
                self.add_error('description', 'Опишите происшествие.')

        return cleaned_data


class OfficialNotificationForm(forms.ModelForm):
    """
    Форма создания официального оповещения (для организаций).
    Отправляется со статусом PENDING на модерацию администратору.
    """
    category = forms.ChoiceField(
        choices=OFFICIAL_CATEGORIES,
        label="Категория объявления",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition text-sm'
        })
    )

    class Meta:
        model = Announcement
        fields = [
            'category',
            'title',
            'description',
            'village',
            'expire_date',
            'is_important',
            'image',
        ]
        labels = {
            'title': 'Заголовок официального сообщения',
            'description': 'Текст официального сообщения',
            'village': 'Населённый пункт',
            'expire_date': 'Дата и время окончания действия (необязательно)',
            'is_important': 'Отметить как важное (срочное оповещение служб)',
            'image': 'Прикрепить документ или фото (необязательно)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition text-sm',
                'placeholder': 'Например: Плановое отключение электроэнергии 25 августа'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition text-sm',
                'rows': 4,
                'placeholder': 'Укажите улицы, причину отключения, время возобновления подачи...'
            }),
            'village': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition text-sm',
                'placeholder': 'с. Кабанбай'
            }),
            'expire_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition text-sm',
                'type': 'datetime-local'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded text-amber-600 focus:ring-amber-500 border-slate-300'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-amber-100 file:text-amber-900 hover:file:bg-amber-200 cursor-pointer',
                'accept': 'image/*'
            }),
        }
