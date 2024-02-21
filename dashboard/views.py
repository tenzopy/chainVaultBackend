from django.shortcuts import render,HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from blockchain.views import blockchain,merkle_tree
from hash_table.views import DHT
from ipfs.views import ipfs
import pyAesCrypt
import os
from .assets import *
from django.contrib.auth.decorators import login_required


fs = FileSystemStorage()

@login_required(login_url='home')
def dash(request):
    return HttpResponse(f"<h2>Hai, {request.user.email}</h2><a href='/dashboard/upload/'>upload</a><br><br><a href='/dashboard/download/'>download</a><br><br><a href='/account/logout/'>logout</a>")


@login_required(login_url='home')
def upload(request):
    if request.method == 'POST' and request.FILES['uploadFile']:
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
        _merkle_input = merkle_input(request.user.email, filename, request.user.email, 'False', '', checksum, encrypted_checksum, ipfs_cid)
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()
        
        # Add to Blockchain
        block = blockchain.mine_block({"merkle_hash" : merkle_hash})

        # Add to Distributed Hash Table
        DHT.store_file(request.user.email, filename, hashTableDataDict(request.user.email, 'False', '', checksum, encrypted_checksum, ipfs_cid))

        # Remove the files from server
        os.remove(file_path)
        os.remove(encrypted_file_path)

        return render(request, 'uploadz.html', {
            'ipfs_cid' : ipfs_cid
        })
    
    return render(request, 'uploadz.html')


@login_required(login_url='home')
def download(request):
    if request.method == 'POST':
        cid, password = request.POST.get('CID'), request.POST.get('password')

        # Download from IPFS
        encrypted_file_name = randomName(6) + ".aes"
        ipfs.download_from_ipfs(cid,encrypted_file_name)

        # AES Decryption
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, encrypted_file_name)
        file_path = os.path.join(settings.MEDIA_ROOT,"bling.jpg")
        pyAesCrypt.decryptFile(encrypted_file_path, file_path, password)

        # Remove files from server
        os.remove(encrypted_file_path)

        return render(request, 'downloadz.html', {
            'download_url': fs.url('bling.jpg')
        })
    
    return render(request, 'downloadz.html')

def share(request):
    pass