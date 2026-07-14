from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin-panel/', include('panel.urls', namespace='panel')),
    path('robots.txt', core_views.robots_txt),
    path('sitemap.xml', core_views.sitemap_xml),
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
