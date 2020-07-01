from django.urls import path

from . import views

urlpatterns = [
    path('', views.show_items, name='show_items'),
    path('items', views.items, name='items'),
    path('items/<int:pk>', views.item_info, name='item_info'),
    path('sign_in', views.sign_in, name='sign_in'),
]