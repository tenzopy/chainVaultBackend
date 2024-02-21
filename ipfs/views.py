from django.shortcuts import render

# Create your views here.
from .ipfs import IPFS
from django.conf import settings

ipfs = IPFS('ip4',settings.ALLOWED_HOSTS[0],5001)

