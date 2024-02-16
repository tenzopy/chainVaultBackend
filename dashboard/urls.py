from django.urls import path

from .views import dash,upload,download,share

urlpatterns = [
    path('',dash,name='dashboard'),
    path('upload/',upload),
    path('download/',download),
    path('share/',share),
]