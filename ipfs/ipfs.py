import ipfshttpclient as _ipfs
from django.conf import settings
import os
from hash_table.views import DHT
import requests
import shutil
from pathlib import Path

MEDIA_ROOT = settings.MEDIA_ROOT
BASE_DIR = settings.BASE_DIR

class IPFS:
    def __init__(self, protocol: str, ip: str, port: int) -> None:
        self.protocol = protocol
        self.ip = ip
        self.port = port
        try:
            self.client = _ipfs.connect(f'/{self.protocol}/{self.ip}/tcp/{self.port}',timeout=20)
        except:
            print("IPFS daemon is not running!")
            exit()
        self.location = MEDIA_ROOT

    def upload_to_ipfs(self, file: str) -> str:
        file_path = os.path.join(MEDIA_ROOT,file)
        response = self.client.add(file_path)
        file_hash = response['Hash']
        return file_hash
    
    def download_from_ipfs(self, cid: str,file_name: str) -> None:
        try:
            self.client.get(cid = cid)
            shutil.move(BASE_DIR / cid,MEDIA_ROOT+'/'+file_name)
            return True
        except _ipfs.exceptions.TimeoutError as e:
            return False
    
    def cache_file(self,cid: str) -> bool:
        self.client.cat(cid = cid)
        return True
    
    def broadcast_file(self, cid: str) -> bool:

        try:
            json_data = {
                "cid" : cid,
            }
            url_successor = f"https://{DHT.successor}/ipfs/cache_file/"  
            requests.post(url_successor, json=json_data, timeout=3, verify='/etc/ssl/self-signed-ca-cert.crt')  

            url_predecessor = f"https://{DHT.predecessor}/ipfs/cache_file/"  
            requests.post(url_predecessor, json=json_data, timeout=3, verify='/etc/ssl/self-signed-ca-cert.crt') 
        except:
            print("Successor or predecessor is unavailable for IPFS Caching.")
