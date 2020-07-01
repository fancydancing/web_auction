from django.contrib import admin
from django.urls import include, path
# from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('auction/', include('auction.urls')),
    path('admin/', admin.site.urls),
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += staticfiles_urlpatterns()

# print(settings.STATIC_ROOT)
print(settings.STATICFILES_DIRS)