from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('items', views.items_view, name='items'),
    path('items/<int:pk>', views.item_info_view, name='item_info'),
    path('items/<int:pk>/bids', views.item_bids_view, name='item_bids'),
    path('items/<int:pk>/auto_bid', views.item_set_autobid, name='item_set_autobid'),
    path('users/bids', views.user_bids, name='user_bids'),
    path('users/<int:pk>', views.user_info_view, name='user_info_view'),
    path('users/<int:pk_user>/item/<int:pk_item>', views.item_info_for_user, name='item_info_for_user'),
    path('sign_in', views.sign_in_view, name='sign_in'),
]
