from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import Announcement


def notification_list(request):
    """Отображение списка всех активных и непросроченных официальных объявлений"""
    selected_category = request.GET.get('category', '').strip()
    
    now = timezone.now()
    announcements = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE
    ).filter(
        Q(expire_date__isnull=True) | Q(expire_date__gt=now)
    )
    
    if selected_category:
        announcements = announcements.filter(category=selected_category)
        
    announcements = announcements.order_by('-is_pinned', '-publish_date')

    context = {
        'announcements': announcements,
        'selected_category': selected_category,
        'categories': Announcement.Category.choices,
    }
    return render(request, 'notifications/list.html', context)

