from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.users.models import Role
from .models import Announcement
from .forms import UrgentNotificationForm, OfficialNotificationForm


def notification_list(request):
    """Отображение списка всех активных и непросроченных оповещений аула"""
    selected_category = request.GET.get('category', '').strip()
    selected_type = request.GET.get('type', '').strip()
    
    now = timezone.now()
    announcements = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE
    ).filter(
        Q(expire_date__isnull=True) | Q(expire_date__gt=now)
    )
    
    if selected_category:
        announcements = announcements.filter(category=selected_category)
        
    if selected_type == 'urgent':
        announcements = announcements.filter(announcement_type=Announcement.AnnouncementType.URGENT)
    elif selected_type == 'official':
        announcements = announcements.filter(announcement_type=Announcement.AnnouncementType.OFFICIAL)
        
    # Срочные и закрепленные первыми
    announcements = announcements.order_by('-is_pinned', '-is_important', '-publish_date')

    # Считаем количество активных
    urgent_count = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE,
        announcement_type=Announcement.AnnouncementType.URGENT
    ).count()

    official_count = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE,
        announcement_type=Announcement.AnnouncementType.OFFICIAL
    ).count()

    can_create_official = False
    if request.user.is_authenticated:
        can_create_official = request.user.role in [Role.ORGANIZATION, Role.ADMIN] or request.user.is_staff or request.user.is_superuser

    context = {
        'announcements': announcements,
        'selected_category': selected_category,
        'selected_type': selected_type,
        'urgent_count': urgent_count,
        'official_count': official_count,
        'can_create_official': can_create_official,
        'categories': Announcement.Category.choices,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def create_urgent_view(request):
    """
    Создание СРОЧНОГО оповещения (пропал ребенок, пожар, авария, опасность).
    Доступно любому авторизованному пользователю.
    Публикуется СРАЗУ (ACTIVE) без предварительной модерации.
    """
    initial_category = request.GET.get('category', Announcement.Category.MISSING_CHILD)

    if request.method == 'POST':
        form = UrgentNotificationForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.announcement_type = Announcement.AnnouncementType.URGENT
            announcement.status = Announcement.Status.ACTIVE  # Публикуется СРАЗУ!
            announcement.is_important = True  # Высокий приоритет
            announcement.publish_date = timezone.now()
            announcement.save()

            messages.success(
                request,
                '🚨 Срочное происшествие опубликовано и сразу доступно всем жителям!'
            )
            return redirect('notifications:list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UrgentNotificationForm(initial={'category': initial_category})

    return render(request, 'notifications/create_urgent.html', {
        'form': form,
        'initial_category': initial_category,
    })


@login_required
def create_official_view(request):
    """
    Создание ОФИЦИАЛЬНОГО оповещения (отключение света, воды, дорожные работы).
    Доступно ТОЛЬКО проверенным организациям и администраторам.
    После отправки получает статус PENDING (на модерации администратора).
    """
    is_org_or_admin = (
        request.user.role in [Role.ORGANIZATION, Role.ADMIN]
        or request.user.is_staff
        or request.user.is_superuser
    )

    if not is_org_or_admin:
        messages.error(
            request,
            'Только проверенные организации могут публиковать официальные оповещения. Подайте заявку на статус организации в профиле.'
        )
        return redirect('notifications:list')

    if request.method == 'POST':
        form = OfficialNotificationForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.announcement_type = Announcement.AnnouncementType.OFFICIAL
            
            # Если отправляет организация — статус PENDING, если суперпользователь — можно сразу ACTIVE
            if request.user.is_superuser or request.user.is_staff:
                announcement.status = Announcement.Status.ACTIVE
                messages.success(request, '📢 Официальное объявление успешно опубликовано!')
            else:
                announcement.status = Announcement.Status.PENDING
                messages.success(
                    request,
                    '📢 Официальное объявление отправлено на модерацию администратору. После проверки оно будет опубликовано.'
                )

            announcement.publish_date = timezone.now()
            announcement.save()
            return redirect('notifications:list')
        else:
            messages.error(request, 'Пожалуйста, проверьте введённые данные.')
    else:
        form = OfficialNotificationForm(initial={'village': 'с. Кабанбай'})

    return render(request, 'notifications/create_official.html', {
        'form': form,
    })


@login_required
def create_choice_view(request):
    """
    Страница диспетчеризации выбора типа создаваемого оповещения.
    """
    is_org_or_admin = (
        request.user.role in [Role.ORGANIZATION, Role.ADMIN]
        or request.user.is_staff
        or request.user.is_superuser
    )

    # Если обычный житель или мастер — сразу отправляем на создание срочного
    if not is_org_or_admin:
        return redirect('notifications:create_urgent')

    return render(request, 'notifications/create_choice.html')


@login_required
def delete_notification_view(request, pk):
    """Удаление или архивация оповещения автором или администратором"""
    announcement = get_object_or_404(Announcement, pk=pk)

    # Проверка прав: автор или администратор
    is_admin = request.user.is_staff or request.user.is_superuser or request.user.role == Role.ADMIN
    if announcement.user != request.user and not is_admin:
        raise PermissionDenied("У вас нет прав для удаления этой записи.")

    if request.method == 'POST':
        announcement.status = Announcement.Status.ARCHIVED
        announcement.save()
        messages.success(request, 'Оповещение перенесено в архив.')
        return redirect('notifications:list')

    return render(request, 'notifications/confirm_delete.html', {'announcement': announcement})
