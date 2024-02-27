from django.urls import path
from .views import cache_file

urlpatterns = [
    path('cache_file/',cache_file),
]