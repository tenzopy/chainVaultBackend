from django.shortcuts import render

from .dht import DHTNode

from django.conf import settings

dhtnode = DHTNode(settings.ALLOWED_HOSTS[0],8000)

# Create your views here.
