from django.urls import path

from .views import AboutProjectView

app_name = 'about'

urlpatterns = [
    path('project/', AboutProjectView.as_view(), name='about_project'),
]
