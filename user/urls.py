from django.urls import path
from .views import signout

urlpatterns = [
    path('logout/', signout, name='logout'),

]