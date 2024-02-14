from django.urls import path

from .views import dash

urlpatterns = [
    path('',dash,name='dashboard')
]