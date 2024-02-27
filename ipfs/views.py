from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import os
from .ipfs import IPFS
from django.conf import settings
from dotenv import load_dotenv,find_dotenv


load_dotenv(find_dotenv())

ipfs = IPFS('ip4',os.environ.get("IPFS_IP_ADDRESS"),5001)


@api_view(['POST'])
def cache_file(request):

    data = request.data
    cid = data['cid']
    
    if ipfs.cache_file(cid):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)