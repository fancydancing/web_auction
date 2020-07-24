from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('items', views.items_view, name='items'),
    path('items/<int:pk>', views.item_info_view, name='item_info'),
    path('items/<int:pk>/bids', views.item_bids_view, name='item_bids'),
    path('items/<int:pk>/auto_bid', views.item_set_autobid, name='item_set_autobid'),
    path('user/bids', views.user_bids, name='user_bids'),
    path('sign_in', views.sign_in_view, name='sign_in'),
]
