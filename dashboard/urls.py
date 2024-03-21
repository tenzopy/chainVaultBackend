from django.urls import path

from .views import dashboard,upload,cloud,share,download

urlpatterns = [
    path('',cloud,name='cloud'),
    path('upload/',upload, name="upload"),
    path('download/',download, name="download"),
    path('share/',share),
]