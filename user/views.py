from django.contrib.auth import logout
from django.urls import reverse
from django.shortcuts import redirect
# Create your views here.

def signout(request):
    logout(request)
    return redirect(reverse('home'))
