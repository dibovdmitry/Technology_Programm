from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('feedback/', include('feedback.urls')),
    path('users/', include('users.urls')),
    path('', include('studies_check.urls')),
    path('', include('django.contrib.auth.urls')),
    path('upload_lab/<int:load_id>/<int:lab_number>/', views.upload_lab, name='upload_lab'),
    path('run_ai_check/<int:lab_id>/', views.run_ai_check, name='run_ai_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
