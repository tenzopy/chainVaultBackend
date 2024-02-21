from django.shortcuts import render,HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from blockchain.views import blockchain
from hash_table.views import DHT
from ipfs.views import ipfs
import pyAesCrypt
import os

fs = FileSystemStorage()

def dash(request):

    blockchain.replace_chain(),
    print(DHT.data)

def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        password = request.POST.get('password')
        filename = fs.save(myfile.name, myfile)
        pyAesCrypt.encryptFile(os.path.join(settings.MEDIA_ROOT,filename), os.path.join(settings.MEDIA_ROOT,filename+ ".aes"), password)
        ipfs_cid = ipfs.upload_to_ipfs(os.path.join(settings.MEDIA_ROOT,filename+ ".aes"))
        os.remove(os.path.join(settings.MEDIA_ROOT, filename))
        os.remove(os.path.join(settings.MEDIA_ROOT, filename+ ".aes"))
        return render(request, 'uploadz.html', {
            'ipfs_cid' : ipfs_cid
        })
    return render(request, 'uploadz.html')

def download(request):
    if request.method == 'POST':
        cid = request.POST.get('CID')
        password = request.POST.get('password')
        ipfs.download_from_ipfs(cid,'bling.aes')
        pyAesCrypt.decryptFile(os.path.join(settings.MEDIA_ROOT, "bling.aes"), os.path.join(settings.MEDIA_ROOT,"bling.jpg"), password)
        os.remove(os.path.join(settings.MEDIA_ROOT, "bling.aes"))
        return render(request, 'downloadz.html', {
            'download_url': fs.url('bling.jpg')
        })
    return render(request, 'downloadz.html')

def share(request):
    pass