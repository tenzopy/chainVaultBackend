import hashlib
from blockchain.views import blockchain
from django.conf import settings
import requests

ip = settings.ALLOWED_HOSTS[0]


class distributedHashTable:

    def __init__(self) -> None: 
        self.data = dict() 
        self.ip = ip
        self.successor = self.get_successor()
        self.predecessor = self.get_predecessor()
    
    def hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get_successor(self) -> str:
        successor = None
        blockchain.update_nodes()
        if self.ip in blockchain.nodes:
            successor =  blockchain.nodes[(blockchain.nodes.index(self.ip) + 1) % len(blockchain.nodes)]
        if successor == self.ip:
            successor = None
        return successor
    
    def get_predecessor(self) -> str:
        predecessor = None
        blockchain.update_nodes()
        if self.ip in blockchain.nodes:
            predecessor =  blockchain.nodes[(blockchain.nodes.index(self.ip) - 1) % len(blockchain.nodes)]
        if predecessor == self.ip:
            predecessor = None
        return predecessor
    
    def does_user_exist(self, key: str) -> bool:
        if key in self.data.keys():
            return True
        return False 

    def add_user(self, key: str) -> bool:
        self.data[key] = {} 
        return True
    
    def does_file_exist(self, key: str, file_name: str) -> bool:
        if file_name in self.data[key].keys():
            return True
        return False
    
    def broadcast_filedata(self,key: str, file_name: str, data: dict) -> None:
        try:
            json_data = {
                "key" : key,
                "file_name" : file_name,
                "data" : data
            }
            url_successor = f"https://{self.successor}/hashtable/post_file"  
            requests.post(url_successor, json=json_data, timeout=3)  

            url_predecessor = f"https://{self.predecessor}/hashtable/post_file"  
            requests.post(url_predecessor, json=json_data, timeout=3) 
        except:
            print("Successor or predecessor is unavailable")


    def broadcast_userdata(self,key: str,data: dict) -> None:
        try:
            json_data = {
                "key" : key,
                "data" : data
            }
            url_successor = f"https://{self.successor}/hashtable/post_userdata"  
            requests.post(url_successor, json=json_data, timeout=3)  

            url_predecessor = f"https://{self.predecessor}/hashtable/post_userdata"  
            requests.post(url_predecessor, json=json_data, timeout=3) 
        except:
            print("Successor or predecessor is unavailable")

    def store_user(self,key: str,data: dict) -> bool:
        if not self.does_user_exist(key):
            self.data[key] = data
            self.broadcast_userdata(key,data)
            return True
        return False

    def store_file(self, key: str, file_name: str, data: dict) -> bool:
        if not self.does_user_exist(key):
            self.add_user(key) 
        if self.does_file_exist(key,file_name):
            return False
        self.data[key][file_name] = data
        self.broadcast_filedata(key,file_name,data)
        return True
    
    def remove_file(self,key: str,file_name: str) -> bool:
        if self.does_user_exist(key) and self.does_file_exist(key,file_name):
            self.data[key].pop(file_name)
            return True
        return False

    def remove_user(self,key: str) -> bool:
        if self.does_user_exist(key):
            self.data.pop(key)
            return True
        return False
    
    def retrieve_file(self,key: str,file_name: str) -> dict:
        if self.does_user_exist(key) and self.does_file_exist(key,file_name):
            return self.data[key][file_name]
        return {}

    def retrieve_user(self,key: str) -> dict:
        if self.does_user_exist(key):
            return self.data[key]
        return {}

