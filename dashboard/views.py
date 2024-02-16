from django.shortcuts import render,HttpResponse

from blockchain.views import blockchain

from hash_table.views import DHT



def dash(request):

    blockchain.replace_chain()
    print(DHT.data)

def upload(request):
    pass

def download(request):
    pass

def share(request):
    pass