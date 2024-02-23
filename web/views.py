from django.shortcuts import render
from dashboard.views import media_list
import datetime
import os
# Create your views here.

def home(request):
    for _ in media_list.data:
        if _[1] + datetime.timedelta(minutes=30) < datetime.datetime.now():
            os.remove(_[0])
            media_list.data.remove(_)
    return render(request,'html/home.html')