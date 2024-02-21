from random import choices
import string
import hashlib

def randomName(length: int) -> str:
    return ''.join(choices(string.ascii_uppercase + string.ascii_lowercase, k=length))


def cal_checksum(file_path: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def merkle_input(key: str, file_name: str, owner: str, shared: bool, receiver: str, checksum: str, encrypted_checksum: str, ipfs_cid: str):
    return list({
        "key" : key,
        "file_name" : file_name,
        "owner" : owner,
        "shared" : shared,
        "receiver" : receiver,
        "checksum" : checksum,
        "encrypted_checksum" : encrypted_checksum,
        "ipfs_cid" : ipfs_cid
    }.items())


