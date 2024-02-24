from django.shortcuts import render,redirect
from django.urls import reverse
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.core.files.storage import FileSystemStorage
from blockchain.views import blockchain,merkle_tree
from hash_table.views import DHT
from ipfs.views import ipfs
import pyAesCrypt
import os
from .assets import *
from django.contrib.auth.decorators import login_required


fs = FileSystemStorage()

media_list = MediaList()

@login_required(login_url='home')
def dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='home')
def cloud(request):
    user_data = DHT.retrieve_user(request.user.email)
    if user_data == {} and DHT.request_user_from_neighbours(request.user.email):
        user_data = DHT.retrieve_user(request.user.email)

    context = {
        "file_names" : list(user_data.keys())
    }
    return render(request, 'cloud_storage.html', context)

@login_required(login_url='home')
@api_view(['POST'])
def upload(request):
    if request.FILES['uploadFile'] and request.POST.get('password')!= '':
        uploadFile, password = request.FILES['uploadFile'], request.POST.get('password')

        # Save the file locally.
        filename = fs.save(uploadFile.name, uploadFile)

        # Calculate Checksum
        file_path = os.path.join(settings.MEDIA_ROOT,filename)
        checksum = cal_checksum(file_path)

        # AES Encryption
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, randomName(6) + ".aes")
        pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)

        # Calculate Encrypted Checksum
        encrypted_checksum = cal_checksum(encrypted_file_path)
        
        # Upload to IPFS
        ipfs_cid = ipfs.upload_to_ipfs(encrypted_file_path)

        # Calculate merkle hash
        _merkle_input = merkle_input(request.user.email, uploadFile.name, 'False', '', checksum, encrypted_checksum, ipfs_cid)
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()
        
        # Add to Blockchain
        block = blockchain.mine_block({"merkle_hash" : merkle_hash})

        # Add to Distributed Hash Table
        DHT.store_file(request.user.email, uploadFile.name, hashTableDataDict(block['index'], 'False', '', checksum, encrypted_checksum, ipfs_cid))

        # Remove the files from server
        os.remove(file_path)
        os.remove(encrypted_file_path)

        return Response({"status" : "ok"},status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='home')
@api_view(['POST'])
def download(request):
    if request.POST.get('file_name') != '' and request.POST.get('password') != '':
        file_name, password = request.POST.get('file_name'), request.POST.get('password')

        # Retreive File Data From DHT
        file_data = DHT.retrieve_file(request.user.email,file_name)
        if file_data == {} and DHT.request_file_from_neighbours(request.user.email,file_name):
            file_data = DHT.retrieve_file(request.user.email,file_name)

        # Retreive Blockchain
        block_index = file_data["block_index"]
        blockchain.replace_chain()
        block = blockchain.chain[block_index-1]

        # Calculate merkle hash
        _merkle_input = merkle_input(request.user.email, file_name, file_data["shared"], file_data["receiver"], file_data["checksum"], file_data["encrypted_checksum"], file_data["ipfs_cid"])
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()

        # Verify Merkle Hash
        if block["merkle_hash"] != merkle_hash:
            return Response({"status": "Merkle Verification Failed",},status=status.HTTP_400_BAD_REQUEST)

        # Download from IPFS
        encrypted_file_name = randomName(6) + ".aes"
        cid = file_data["ipfs_cid"]
        ipfs.download_from_ipfs(cid,encrypted_file_name)

        # Calculate Encrypted Checksum
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, encrypted_file_name)
        encrypted_checksum = cal_checksum(encrypted_file_path)
        if file_data["encrypted_checksum"] != encrypted_checksum:
            return render(request, 'downloadz.html', {
                "error" : "Checksum Verification Failed."
            })

        # AES Decryption
        file_path = os.path.join(settings.MEDIA_ROOT,file_name)
        try:
            pyAesCrypt.decryptFile(encrypted_file_path, file_path, password)
        except:
            return render(request, 'downloadz.html', {
                "error" : "Wrong Password"
            })

        # Calculate Checksum
        checksum = cal_checksum(file_path)
        if file_data["checksum"] != checksum:
            return render(request, 'downloadz.html', {
                "error" : "Checksum Verification Failed."
            })

        # Remove files from server
        os.remove(encrypted_file_path)
        media_list.add(file_path)

        return Response({"status": "ok","download_url": fs.url(file_name)},status=status.HTTP_200_OK)

def share(request):
    pass