from django.shortcuts import render
from django.http import Http404
from .models import DirectoryEntry

# Метаданные оформления для категорий в стиле AUL
CATEGORY_META = {
    DirectoryEntry.Category.EMERGENCY: {'icon': 'e911_emergency', 'color': 'text-red-600', 'bg': 'bg-red-50', 'border': 'border-red-200'},
    DirectoryEntry.Category.UTILITIES: {'icon': 'water_drop', 'color': 'text-blue-600', 'bg': 'bg-blue-50', 'border': 'border-blue-200'},
    DirectoryEntry.Category.MASTERS: {'icon': 'construction', 'color': 'text-amber-600', 'bg': 'bg-amber-50', 'border': 'border-amber-200'},
    DirectoryEntry.Category.ORGANIZATIONS: {'icon': 'account_balance', 'color': 'text-purple-600', 'bg': 'bg-purple-50', 'border': 'border-purple-200'},
    DirectoryEntry.Category.SHOPS: {'icon': 'shopping_bag', 'color': 'text-emerald-600', 'bg': 'bg-emerald-50', 'border': 'border-emerald-200'},
    DirectoryEntry.Category.PHARMACIES: {'icon': 'medication', 'color': 'text-teal-600', 'bg': 'bg-teal-50', 'border': 'border-teal-200'},
    DirectoryEntry.Category.SCHOOLS: {'icon': 'school', 'color': 'text-indigo-600', 'bg': 'bg-indigo-50', 'border': 'border-indigo-200'},
    DirectoryEntry.Category.HOSPITALS: {'icon': 'local_hospital', 'color': 'text-rose-600', 'bg': 'bg-rose-50', 'border': 'border-rose-200'},
    DirectoryEntry.Category.TAXI: {'icon': 'local_taxi', 'color': 'text-yellow-600', 'bg': 'bg-yellow-50', 'border': 'border-yellow-200'},
    DirectoryEntry.Category.CAFE: {'icon': 'restaurant', 'color': 'text-orange-600', 'bg': 'bg-orange-50', 'border': 'border-orange-200'},
    DirectoryEntry.Category.OTHER: {'icon': 'grid_view', 'color': 'text-slate-600', 'bg': 'bg-slate-50', 'border': 'border-slate-200'},
}


def directory_list(request):
    """Экран категорий справочника (выбор категории)"""
    active_entries = DirectoryEntry.objects.filter(
        status=DirectoryEntry.Status.ACTIVE
    )

    categories = []
    for cat_code, cat_label in DirectoryEntry.Category.choices:
        count = active_entries.filter(category=cat_code).count()
        meta = CATEGORY_META.get(
            cat_code,
            {'icon': 'folder', 'color': 'text-purple-600', 'bg': 'bg-purple-50', 'border': 'border-purple-200'}
        )
        categories.append({
            'code': cat_code,
            'name': cat_label,
            'icon': meta['icon'],
            'color': meta['color'],
            'bg': meta['bg'],
            'border': meta['border'],
            'count': count
        })

    context = {
        'categories': categories,
        'total_count': active_entries.count()
    }
    return render(request, 'directory/list.html', context)


def directory_category(request, category_slug):
    """Страница выбранной категории с контактами"""
    category_choices = dict(DirectoryEntry.Category.choices)
    if category_slug not in category_choices:
        raise Http404("Категория не найдена")

    category_name = category_choices[category_slug]
    meta = CATEGORY_META.get(
        category_slug,
        {'icon': 'folder', 'color': 'text-purple-600', 'bg': 'bg-purple-50', 'border': 'border-purple-200'}
    )

    entries = DirectoryEntry.objects.filter(
        category=category_slug,
        status=DirectoryEntry.Status.ACTIVE
    ).order_by('-priority', 'name')

    context = {
        'category_code': category_slug,
        'category_name': category_name,
        'meta': meta,
        'entries': entries,
        'entries_count': entries.count()
    }
    return render(request, 'directory/category.html', context)
