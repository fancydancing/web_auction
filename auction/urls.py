from django.urls import path

from . import views

urlpatterns = [
    path('', views.show_items, name='show_items'),
    path('items', views.items, name='items'),
    path('items/<int:pk>', views.item_update, name='item_update'),
]