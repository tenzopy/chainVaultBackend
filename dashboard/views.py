from django.shortcuts import render,HttpResponse

from blockchain.views import blockchain


def dash(request):
    return HttpResponse(request.user.email)