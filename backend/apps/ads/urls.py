from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.ad_list, name='list'),
    path('my/', views.ad_my_list, name='my_list'),
    path('create/', views.ad_create, name='create'),
    path('<int:ad_id>/edit/', views.ad_edit, name='edit'),
    path('<int:ad_id>/delete/', views.ad_delete, name='delete'),
]

