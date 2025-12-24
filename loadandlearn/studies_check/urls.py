from django.urls import path

from .views import *

app_name = 'studies_check'


urlpatterns = [
    path('', store, name='home'),
    path('departments/', departments, name='departments'),
    path('department/<slug:dept_slug>/', department_detail, name='department_detail'),
]
