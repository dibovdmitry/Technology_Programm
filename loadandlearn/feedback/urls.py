from django.urls import path

from .views import FeedBackPathView

app_name = 'feedback'

urlpatterns = [
    path('feedba/', FeedBackPathView.as_view(), name='feedback_feedba'),
]
