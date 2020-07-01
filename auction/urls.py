from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('items/', views.items_list, name='items_list'),
]