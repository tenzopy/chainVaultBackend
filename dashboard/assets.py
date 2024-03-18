from random import choices
import string
import hashlib
from datetime import datetime


class MediaList:
    def __init__(self) -> None:
        self.data = list()

    def add(self,file_path: str) -> bool:
        self.data.append((file_path,datetime.now()))

def randomName(length: int) -> str:
    return ''.join(choices(string.ascii_uppercase + string.ascii_lowercase, k=length))


def cal_checksum(file_path: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def merkle_input(key: str, file_name: str, shared: str, sender: str, receiver: str, checksum: str, encrypted_checksum: str, ipfs_cid: str):
    return [key, file_name, shared, sender, receiver, checksum, encrypted_checksum, ipfs_cid]

def hashTableDataDict(block_index: int, shared: str, sender: str, receiver: str, checksum: str, encrypted_checksum: str, ipfs_cid: str) -> dict:
    return {
        "block_index" : block_index,
        "shared" : shared,
        "sender" : sender,
        "receiver" : receiver,
        "checksum" : checksum,
        "encrypted_checksum" : encrypted_checksum,
        "ipfs_cid" : ipfs_cid,
    }