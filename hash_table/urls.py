from django.urls import path
from .views import get_userdata,get_file,post_file,post_userdata,delete_file,delete_user

urlpatterns = [
    path('get_userdata',get_userdata),
    path('get_file',get_file),
    path('post_file',post_file),
    path('post_userdata',post_userdata),
    path('delete_file',delete_file),
    path('delete_user',delete_user),

]