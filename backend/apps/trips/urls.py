from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.trip_list, name='list'),
    path('my/', views.trip_my_list, name='my_list'),
    path('create/', views.trip_create, name='create'),
    path('<int:trip_id>/edit/', views.trip_edit, name='edit'),
    path('<int:trip_id>/delete/', views.trip_delete, name='delete'),
]

