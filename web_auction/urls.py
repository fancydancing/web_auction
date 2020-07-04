from django.urls import include, path

urlpatterns = [
    path('', include('auction.urls')),
    path('api/', include('auction.urls')),
]