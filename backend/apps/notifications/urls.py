from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('create/', views.create_choice_view, name='create'),
    path('create/urgent/', views.create_urgent_view, name='create_urgent'),
    path('create/official/', views.create_official_view, name='create_official'),
    path('<int:pk>/delete/', views.delete_notification_view, name='delete'),
]
