from django.contrib import admin
from django.urls import include, path
# from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('', include('auction.urls')),
    path('api/', include('auction.urls')),
]