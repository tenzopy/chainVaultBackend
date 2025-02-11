from django.shortcuts import render,redirect,HttpResponse
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
import validators
import os
from .assets import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime
import magic


fs = FileSystemStorage()

media_list = MediaList()

@login_required(login_url='home')
def dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='home')
def cloud(request):
    user_data = DHT.retrieve_user(request.user.email)
    blockchain.replace_chain()
    if user_data == {} and DHT.request_user_from_neighbours(request.user.email):
        user_data = DHT.retrieve_user(request.user.email)
    File_size = 0
    for key,values in user_data.items():
        File_size+=int(values['file_size'])
    context = {
        "file" : user_data,
        "File_size" : format_bytes(File_size),
    }
    return render(request, 'cloud_storage.html', context)

@login_required(login_url='home')
@api_view(['POST'])
def upload(request):
    if request.FILES.get('uploadFile',False) and request.POST.get('password')!= '':
        uploadFile, password = request.FILES['uploadFile'], request.POST.get('password')

        # Save the file locally.
        filename = fs.save(uploadFile.name, uploadFile)

        # Calculate Checksum
        file_path = os.path.join(settings.MEDIA_ROOT,filename)
        checksum = cal_checksum(file_path)

        #Calculate File Info
        fileSize = os.stat(file_path).st_size
        fileCreated = datetime.now().timestamp() * 1000
        fileType = magic.from_file(file_path, mime = True)

        # AES Encryption
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, randomName(6) + ".aes")
        pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)

        # Calculate Encrypted Checksum
        encrypted_checksum = cal_checksum(encrypted_file_path)
        
        # Upload to IPFS
        ipfs_cid = ipfs.upload_to_ipfs(encrypted_file_path)

        # Calculate merkle hash
        _merkle_input = merkle_input(request.user.email, uploadFile.name, fileSize, fileCreated, fileType, 'False', '', '', checksum, encrypted_checksum, ipfs_cid)
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()
        
        # Add to Blockchain
        block = blockchain.mine_block({"merkle_hash" : merkle_hash})

        # Add to Distributed Hash Table
        DHT.store_file(request.user.email, uploadFile.name, hashTableDataDict(block['index'], fileSize, fileCreated, fileType, 'False', '', '', checksum, encrypted_checksum, ipfs_cid))

        # Cache to Nearby IPFS
        ipfs.broadcast_file(ipfs_cid)

        # Remove the files from server
        os.remove(file_path)
        os.remove(encrypted_file_path)

        return Response({
            "status" : "ok",
            "file_size" : fileSize,
            "file_created" : fileCreated,
            "file_type" : fileType,
        },status=status.HTTP_200_OK)
    
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
        if file_data["shared"] == "True":
            user = file_data["receiver"]
        else:
            user = request.user.email
        _merkle_input = merkle_input(user, file_name, file_data["file_size"], file_data["file_created"], file_data["file_type"], file_data["shared"], file_data["sender"], file_data["receiver"], file_data["checksum"], file_data["encrypted_checksum"], file_data["ipfs_cid"])
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()

        # Verify Merkle Hash
        if block["merkle_hash"] != merkle_hash:
            return Response({"status": "Merkle Verification Failed",},status=status.HTTP_200_OK)

        # Download from IPFS
        encrypted_file_name = randomName(6) + ".aes"
        cid = file_data["ipfs_cid"]
        if not ipfs.download_from_ipfs(cid,encrypted_file_name):
            # Send E-Mail with password to receiver   
            Subject = "ChainVault, Your file is no longer available. "
            HTML_Message = render_to_string('email_not_found.html', {

            'file_name' : file_name,
            'sender' : file_data["sender"], 

            })

            Plain_Message = render_to_string('email_not_found_plain.html', {

            'file_name' : file_name,
            'sender' : file_data["sender"], 

            })

            send_mail(Subject, Plain_Message, from_email="noreply@sliceit.me", recipient_list=[file_data["sender"]], html_message=HTML_Message, fail_silently=True)

            return Response({"status": "File Not Found!",},status=status.HTTP_200_OK)
        
        # Calculate Encrypted Checksum
        encrypted_file_path = os.path.join(settings.MEDIA_ROOT, encrypted_file_name)
        encrypted_checksum = cal_checksum(encrypted_file_path)
        if file_data["encrypted_checksum"] != encrypted_checksum:
            os.remove(encrypted_file_path)
            return Response({"status": "Checksum Verification Failed",},status=status.HTTP_200_OK)

        # AES Decryption
        file_path = os.path.join(settings.MEDIA_ROOT,file_name)
        try:
            pyAesCrypt.decryptFile(encrypted_file_path, file_path, password)
        except:
            os.remove(encrypted_file_path)
            return Response({"status": "Wrong Password",},status=status.HTTP_200_OK)
        
        # Calculate Checksum
        checksum = cal_checksum(file_path)
        if file_data["checksum"] != checksum:
            os.remove(encrypted_file_path)
            os.remove(file_path)
            return Response({"status": "Checksum Verification Failed",},status=status.HTTP_200_OK)

        # Remove files from server
        os.remove(encrypted_file_path)
        media_list.add(file_path)

        return Response({"status": "ok","download_url": fs.url(file_name)},status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='home')
@api_view(['POST'])
def share(request):

    if request.method == 'POST' and request.POST.get('password') != '' and validators.email(request.POST.get('receiver')):

        # Retreiving Data
        password = request.POST.get('password')
        sender = request.user.email
        receiver = request.POST.get('receiver')

        if request.FILES.get('uploadFile',False):

            uploadFile, password = request.FILES['uploadFile'], request.POST.get('password')

            # Save the file locally.
            filename = fs.save(uploadFile.name, uploadFile)

            # Calculate Checksum
            file_path = os.path.join(settings.MEDIA_ROOT,filename)
            checksum = cal_checksum(file_path)

            #Calculate File Info
            fileSize = os.stat(file_path).st_size
            fileCreated = datetime.now().timestamp() * 1000
            fileType = magic.from_file(file_path, mime = True)

            # AES Encryption
            encrypted_file_path = os.path.join(settings.MEDIA_ROOT, randomName(6) + ".aes")
            pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)

            # Calculate Encrypted Checksum
            encrypted_checksum = cal_checksum(encrypted_file_path)
            
            # Upload to IPFS
            ipfs_cid = ipfs.upload_to_ipfs(encrypted_file_path)

            # Calculate merkle hash
            _merkle_input = merkle_input(request.user.email, uploadFile.name, fileSize, fileCreated, fileType, 'True', sender, receiver, checksum, encrypted_checksum, ipfs_cid)
            merkle_tree.makeTreeFromArray(_merkle_input)
            merkle_hash = merkle_tree.calculateMerkleRoot()
            
            # Add to Blockchain
            block = blockchain.mine_block({"merkle_hash" : merkle_hash})

            # Add to Distributed Hash Table
            DHT.store_file(request.user.email, uploadFile.name, hashTableDataDict(block['index'], fileSize, fileCreated, fileType, 'True', request.user.email, request.POST.get('receiver'), checksum, encrypted_checksum, ipfs_cid))

            # Cache to Nearby IPFS
            ipfs.broadcast_file(ipfs_cid)

            # Remove the files from server
            os.remove(file_path)
            os.remove(encrypted_file_path)


        if request.POST.get('file_name')!= None:
            file_name = request.POST.get('file_name')
        else:
            file_name = uploadFile.name

        # Retreive File Data From DHT
        file_data = DHT.retrieve_file(sender, file_name)
        if file_data == {} and DHT.request_file_from_neighbours(sender, file_name):
            file_data = DHT.retrieve_file(sender, file_name)

        # Retreive Blockchain
        block_index = file_data["block_index"]
        blockchain.replace_chain()
        block = blockchain.chain[block_index-1]

        # Calculate merkle hash
        _merkle_input = merkle_input(sender, file_name, file_data["file_size"], file_data["file_created"], file_data["file_type"], file_data["shared"], file_data["sender"], file_data["receiver"], file_data["checksum"], file_data["encrypted_checksum"], file_data["ipfs_cid"])
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()

        # Verify Merkle Hash
        if block["merkle_hash"] != merkle_hash:
            return Response({"status": "Merkle Verification Failed",},status=status.HTTP_200_OK)
        
        # Expand File Data
        ipfs_cid = file_data['ipfs_cid']
        checksum = file_data['checksum']
        encrypted_checksum = file_data['encrypted_checksum']
        fileSize = file_data["file_size"]
        fileCreated = file_data["file_created"]
        fileType = file_data["file_type"]

        # Calculate merkle hash
        _merkle_input = merkle_input(receiver, file_name, fileSize, fileCreated, fileType, 'True', sender, receiver, checksum, encrypted_checksum, ipfs_cid)
        merkle_tree.makeTreeFromArray(_merkle_input)
        merkle_hash = merkle_tree.calculateMerkleRoot()
        
        # Add to Blockchain
        block = blockchain.mine_block({"merkle_hash" : merkle_hash})

        # Add to Distributed Hash Table (Receiver)
        DHT.store_file(receiver, file_name, hashTableDataDict(block['index'], fileSize, fileCreated, fileType, 'True', sender, receiver, checksum, encrypted_checksum, ipfs_cid))

        # Update Distributed Hash Table (Sender)
        DHT.update_file(sender, file_name, hashTableDataDict(block['index'], fileSize, fileCreated, fileType, 'True', sender, receiver, checksum, encrypted_checksum, ipfs_cid))

        # Cache to Nearby IPFS
        ipfs.broadcast_file(ipfs_cid)
        
        # Send E-Mail with password to receiver   
        Subject = "ChainVault, a file is shared with you."
        HTML_Message = render_to_string('email_password.html', {

        'receiver': receiver,
        'password' : password,
        'file_name' : file_name,
        'sender' : sender, 

        })

        Plain_Message = render_to_string('email_password_plain.html', {

        'receiver': receiver,
        'password' : password,
        'file_name' : file_name,
        'sender' : sender, 

        })

        send_mail(Subject, Plain_Message, from_email="noreply@sliceit.me", recipient_list=[receiver], html_message=HTML_Message, fail_silently=True)


        return Response({
            "status" : "ok",
            "file_size" : fileSize,
            "file_created" : fileCreated,
            "file_type" : fileType,
        },status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='home')
@api_view(['DELETE'])
def delete(request):
    if request.POST.get('file_name') != '':
        file_name = request.POST.get('file_name')
        DHT.remove_file(request.user.email,file_name)
        DHT.broadcast_filedata_deletion(request.user.email,file_name)
        return Response({"status":"ok"},status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)