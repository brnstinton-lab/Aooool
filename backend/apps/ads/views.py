from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ad, AdImage


def ad_list(request):
    """Отображение списка объявлений (доступно всем)"""
    ads = Ad.objects.active().prefetch_related('images')
    return render(request, 'ads/list.html', {'ads': ads})


@login_required
def ad_create(request):
    """Создание нового объявления (требует авторизации)"""
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
                user=request.user,
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

            messages.success(request, 'Объявление успешно опубликовано.')
            return redirect('ads:list')

    return render(request, 'ads/create.html', {
        'ad_types': Ad.AdType.choices,
        'categories': Ad.Category.choices,
        'errors': errors,
        'form_data': form_data,
    })


@login_required
def ad_edit(request, ad_id):
    """Редактирование объявления (только автор или администратор)"""
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user and ad.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для редактирования этого объявления.")
        return redirect('ads:list')

    errors = {}
    form_data = {
        'title': ad.title,
        'ad_type': ad.ad_type,
        'category': ad.category,
        'description': ad.description,
        'phone': ad.phone,
        'price': str(ad.price) if ad.price is not None else '',
        'comment': ad.comment or '',
    }

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

        if not title:
            errors['title'] = 'Укажите заголовок объявления'

        valid_types = [choice[0] for choice in Ad.AdType.choices]
        if ad_type and ad_type not in valid_types:
            errors['ad_type'] = 'Выберите тип объявления'

        valid_categories = [choice[0] for choice in Ad.Category.choices]
        if category and category not in valid_categories:
            errors['category'] = 'Выберите категорию'

        if not description:
            errors['description'] = 'Укажите описание объявления'

        if not phone:
            errors['phone'] = 'Укажите номер телефона'
        else:
            phone_check = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not all(c.isdigit() or c == '+' for c in phone_check):
                errors['phone'] = 'Номер телефона должен содержать только цифры и символ "+"'

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
            ad.title = title
            if ad_type:
                ad.ad_type = ad_type
            if category:
                ad.category = category
            ad.description = description
            ad.phone = phone
            ad.price = price
            ad.comment = comment
            ad.save()

            if uploaded_images:
                for image in uploaded_images:
                    if image:
                        AdImage.objects.create(ad=ad, image=image)

            messages.success(request, 'Объявление успешно обновлено.')
            return redirect('ads:my_list')

    return render(request, 'ads/create.html', {
        'ad_types': Ad.AdType.choices,
        'categories': Ad.Category.choices,
        'errors': errors,
        'form_data': form_data,
        'is_edit': True,
        'ad': ad,
    })


@login_required
def ad_delete(request, ad_id):
    """Удаление объявления (только автор или администратор)"""
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user and ad.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для удаления этого объявления.")
        return redirect('ads:list')

    if request.method == 'POST':
        ad.delete()
        messages.success(request, "Объявление успешно удалено.")
    return redirect('ads:list')


@login_required
def ad_my_list(request):
    """Отображение объявлений текущего пользователя"""
    ads = Ad.objects.filter(user=request.user).order_by('-created_at').prefetch_related('images')
    return render(request, 'ads/my_list.html', {'ads': ads})



