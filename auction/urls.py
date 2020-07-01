from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('items', views.items, name='items'),
    path('base/', views.show_items, name='show_items'),
]