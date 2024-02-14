from django.shortcuts import render,HttpResponse

from blockchain.views import blockchain

from hash_table.views import dhtnode



def dash(request):

    return HttpResponse("hey")