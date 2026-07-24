from django.shortcuts import render

def ad_list(request):
    """Отображение списка объявлений"""
    return render(request, 'ads/list.html')

