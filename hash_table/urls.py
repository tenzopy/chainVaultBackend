from django.urls import path
from .views import get_userdata,get_file,post_file,post_userdata,delete_file,delete_user,update_file,update_userdata,get_dht,fetchData

urlpatterns = [
    path('get_userdata',get_userdata),
    path('get_file',get_file),
    path('post_file',post_file),
    path('post_userdata',post_userdata),
    path('update_file',update_file),
    path('update_userdata',update_userdata),
    path('delete_file',delete_file),
    path('delete_user',delete_user),
    path('get_dht',get_dht),
    path('fetch_data',fetchData),

]