import hashlib
import requests


class DHTNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.data = {}
        self.successor = None
        self.predecessor = None

    def hash_key(self, key):
        return hashlib.sha256(key.encode()).hexdigest()

    def find_successor(self, key_hash):
        if self.successor:
            if self.hash_key(self.successor[0]) > key_hash:
                return self.successor
            else:
                # Forward the request to the successor
                return self.successor[1].find_successor(key_hash)
        else:
            return self.host, self.port

    def store_data(self, key, value):
        key_hash = self.hash_key(key)
        successor_host, successor_port = self.find_successor(key_hash)
        if successor_host == self.host and successor_port == self.port:
            self.data[key] = value
            self.broadcast_data(key, value)
        else:
            # Forward the data to the successor
            requests.post(f"http://{successor_host}:{successor_port}/store_data", json={'key': key, 'value': value})

    def retrieve_data(self, key):
        key_hash = self.hash_key(key)
        successor_host, successor_port = self.find_successor(key_hash)
        if successor_host == self.host and successor_port == self.port:
            return self.data.get(key)
        else:
            # Forward the request to the successor
            response = requests.get(f"http://{successor_host}:{successor_port}/retrieve_data", params={'key': key})
            return response.json()

    def broadcast_data(self, key, value):
        # Broadcast data to other nodes
        for node_host, node_port in [self.successor, self.predecessor]:
            if node_host and node_port:
                requests.post(f"http://{node_host}:{node_port}/store_data", json={'key': key, 'value': value})