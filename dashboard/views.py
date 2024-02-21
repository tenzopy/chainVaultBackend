from django.shortcuts import render,HttpResponse

from django.conf import settings

from django.core.files.storage import FileSystemStorage

from blockchain.views import blockchain

from hash_table.views import DHT

from ipfs.views import ipfs


def dash(request):

    blockchain.replace_chain()
    print(DHT.data)

def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'uploadz.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'uploadz.html')

def download(request):
    pass

def share(request):
    pass