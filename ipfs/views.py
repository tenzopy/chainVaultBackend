from django.shortcuts import render

# Create your views here.
from .ipfs import IPFS

ipfs = IPFS('ip4','100.68.187.138',5001)


def upload(request):
    print(ipfs.upload_to_ipfs('img6.jpg'))
    

def download(request):
    ipfs.download_from_ipfs('QmSmBWDhH2bqFtPUHyAq2yjL9ATVdZ51AbGXpBFbetckiF','akku.jpg')