from django.urls import path

from .views import dashboard,upload,cloud,share,download,delete

urlpatterns = [
    path('',cloud,name='cloud'),
    path('upload/',upload, name="upload"),
    path('download/',download, name="download"),
    path('share/',share),
    path('delete/',delete),
]