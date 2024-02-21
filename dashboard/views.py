from django.shortcuts import render,HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from blockchain.views import blockchain
from hash_table.views import DHT
from ipfs.views import ipfs
import pyAesCrypt
import os
from .assets import *

fs = FileSystemStorage()

def dash(request):

    blockchain.replace_chain(),
    print(DHT.data)

def upload(request):
    if request.method == 'POST' and request.FILES['uploadFile']:
        uploadFile, password = request.FILES['uploadFile'], request.POST.get('password')

        # Save the file locally.
        filename = fs.save(uploadFile.name, uploadFile)

        # AES Encryption
        file_path = os.path.join(settings.MEDIA_ROOT,filename)
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, randomName(6) + ".aes")
        pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)
        
        # Upload to IPFS
        ipfs_cid = ipfs.upload_to_ipfs(encrypted_file_path)

        # Remove the files from server
        os.remove(file_path)
        os.remove(encrypted_file_path)

        return render(request, 'uploadz.html', {
            'ipfs_cid' : ipfs_cid
        })
    
    return render(request, 'uploadz.html')

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