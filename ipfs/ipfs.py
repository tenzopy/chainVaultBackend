import ipfshttpclient as _ipfs
from django.conf import settings
import os

MEDIA_ROOT = settings.MEDIA_ROOT

class IPFS:
    def __init__(self, protocol: str, ip: str, port: int) -> None:
        self.protocol = protocol
        self.ip = ip
        self.port = port
        try:
            self.client = _ipfs.connect(f'/{self.protocol}/{self.ip}/tcp/{self.port}')
        except:
            print("IPFS daemon is not running!")
            exit()
        self.location = MEDIA_ROOT

    def upload_to_ipfs(self, file: str):
        file_path = os.path.join(MEDIA_ROOT,file)
        response = self.client.add(file_path)
        file_hash = response['Hash']
        return file_hash
    
    def download_from_ipfs(self, cid: str,file_name: str):
        self.client.get(cid = cid,target = MEDIA_ROOT)
        os.rename(os.path.join(MEDIA_ROOT,cid),os.path.join(MEDIA_ROOT,file_name))
    
