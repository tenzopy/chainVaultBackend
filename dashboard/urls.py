from django.urls import path

from .views import dash,upload,download,share

urlpatterns = [
    path('',dash,name='dashboard'),
    path('upload/',upload, name="upload"),
    path('download/',download, name="download"),
    path('share/',share),
]