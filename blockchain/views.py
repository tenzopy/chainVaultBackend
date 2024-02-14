from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from blockchain.blockchain import Blockchain

blockchain = Blockchain()


@api_view(['GET'])
def get_chain(request):
    if not blockchain.is_chain_valid(blockchain.chain):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(blockchain.chain)


@api_view(['POST'])
def mine_block(request):
    data = request.data
    blockchain.replace_chain()
    if not blockchain.is_chain_valid(blockchain.chain):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(blockchain.mine_block(data))

@api_view(['GET'])
def is_blockchain_valid(request):
    if not blockchain.is_chain_valid(blockchain.chain):
        return Response({"status": False})
    return Response({"status": True})