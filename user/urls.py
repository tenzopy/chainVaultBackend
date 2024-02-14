from django.urls import path
from .views import signup,signin,signout,activate

urlpatterns = [
    path('signup/', signup,name='signup'),
    path('login/', signin,name='login'),
    path('logout/',signout,name='logout'),
    path('activate/<uidb64>/<token>/',activate, name='activate'),  
]