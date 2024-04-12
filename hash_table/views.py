from django.shortcuts import render,HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hash_table.dht import distributedHashTable

DHT = distributedHashTable()

@api_view(['GET'])
def get_userdata(request):
    key = request.GET.get('key')
    if key in DHT.data.keys():
        return Response(DHT.retrieve_user(key),status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_file(request):
    key = request.GET.get('key')
    file_name = request.GET.get('file_name')
    if key in DHT.data.keys() and file_name in DHT.data[key].keys():
        return Response(DHT.retrieve_file(key,file_name),status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def post_file(request):
    data = request.data
    key,file_name,hash_data = data['key'],data['file_name'],data['data']
    if DHT.store_remote_file(key,file_name,hash_data):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def post_userdata(request):
    data = request.data
    key, userdata = data['key'],data['data']
    if DHT.store_remote_user(key,userdata):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def update_file(request):
    data = request.data
    key,file_name,hash_data = data['key'],data['file_name'],data['data']
    if DHT.update_remote_file(key,file_name,hash_data):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def update_userdata(request):
    data = request.data
    key, userdata = data['key'],data['data']
    if DHT.update_remote_user(key,userdata):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def delete_user(request):
    data = request.data
    key = data['key']
    if DHT.remove_user(key):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def delete_file(request):
    data = request.data
    key = data['key']
    file_name = data['file_name']
    if DHT.remove_file(key,file_name):
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_dht(request):
    return Response(DHT.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def fetchData(request):
    key = request.user.email
    if DHT.fetch_data(key):
        return Response({"status":"ok"},status=status.HTTP_200_OK)
    return Response(status=status.HTTP_304_NOT_MODIFIED)