from django.urls import path
from . import views

app_name = 'directory'

urlpatterns = [
    path('', views.directory_list, name='list'),
    path('category/<str:category_slug>/', views.directory_category, name='category'),
]
