from django.shortcuts import render, redirect
from .models import Ad, AdImage


def ad_list(request):
    """Отображение списка объявлений"""
    ads = Ad.objects.active().prefetch_related('images')
    return render(request, 'ads/list.html', {'ads': ads})


def ad_create(request):
    """Создание нового объявления"""
    errors = {}
    form_data = {}

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        ad_type = request.POST.get('ad_type', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        phone = request.POST.get('phone', '').strip()
        price_raw = request.POST.get('price', '').strip()
        comment = request.POST.get('comment', '').strip()

        form_data = {
            'title': title,
            'ad_type': ad_type,
            'category': category,
            'description': description,
            'phone': phone,
            'price': price_raw,
            'comment': comment,
        }

        # Валидация обязательных полей
        if not title:
            errors['title'] = 'Укажите заголовок объявления'

        valid_types = [choice[0] for choice in Ad.AdType.choices]
        if not ad_type or ad_type not in valid_types:
            errors['ad_type'] = 'Выберите тип объявления'

        valid_categories = [choice[0] for choice in Ad.Category.choices]
        if not category or category not in valid_categories:
            errors['category'] = 'Выберите категорию'

        if not description:
            errors['description'] = 'Укажите описание объявления'

        # Валидация телефона (минимальная проверка)
        if not phone:
            errors['phone'] = 'Укажите номер телефона'
        else:
            phone_check = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not all(c.isdigit() or c == '+' for c in phone_check):
                errors['phone'] = 'Номер телефона должен содержать только цифры и символ "+"'

        # Обработка необязательного поля price
        price = None
        if price_raw:
            try:
                price_val = int(price_raw)
                if price_val >= 0:
                    price = price_val
                else:
                    errors['price'] = 'Укажите корректную цену'
            except ValueError:
                errors['price'] = 'Укажите цену числом'

        # Обработка фотографий
        uploaded_images = request.FILES.getlist('images')
        if len(uploaded_images) > 6:
            errors['images'] = 'Можно загрузить от 1 до 6 фотографий'

        allowed_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        for f in uploaded_images:
            if f and f.name:
                ext = f.name.lower()
                if not ext.endswith(allowed_extensions):
                    errors['images'] = 'Допустимые форматы фотографий: JPG, JPEG, PNG, WEBP'
                    break

        if not errors:
            ad = Ad.objects.create(
                title=title,
                ad_type=ad_type,
                category=category,
                description=description,
                phone=phone,
                price=price,
                comment=comment,
                status=Ad.Status.ACTIVE,
            )

            # Сохранение объектов AdImage для каждой загруженной фотографии
            images = request.FILES.getlist('images')
            for image in images:
                if image:
                    AdImage.objects.create(
                        ad=ad,
                        image=image
                    )

            return redirect('feed')

    return render(request, 'ads/create.html', {
        'ad_types': Ad.AdType.choices,
        'categories': Ad.Category.choices,
        'errors': errors,
        'form_data': form_data,
    })


