from django.urls import path

from .views import dashboard,upload,cloud,share,download

urlpatterns = [
    path('',dashboard,name='dashboard'),
    path('upload/',upload, name="upload"),
    path('download/',download, name="download"),
    path('cloud/',cloud, name="cloud"),
    path('share/',share),
]