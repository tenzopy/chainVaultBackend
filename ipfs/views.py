from django.shortcuts import render

# Create your views here.
import os
from .ipfs import IPFS
from django.conf import settings
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

ipfs = IPFS('ip4',os.environ.get("IPFS_IP_ADDRESS"),5001)

