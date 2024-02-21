from django.urls import path
from .views import upload,download

urlpatterns = [
    path('upload/',upload),
    path('download/',download),

]