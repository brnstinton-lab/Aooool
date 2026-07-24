from django.shortcuts import render

def directory_list(request):
    """Отображение справочника"""
    return render(request, 'directory/list.html')

