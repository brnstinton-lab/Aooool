from django.shortcuts import render
from .models import Announcement


def notification_list(request):
    """Отображение списка всех активных официальных объявлений"""
    selected_category = request.GET.get('category', '').strip()
    
    announcements = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE
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

