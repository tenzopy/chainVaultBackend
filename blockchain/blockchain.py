import datetime as _dt
import hashlib as _hashlib
import json as _json
import requests
from requests.adapters import HTTPAdapter
import os
from dotenv import find_dotenv,load_dotenv

load_dotenv(find_dotenv())

COORDINATION_SERVER = os.environ.get("COORDINATION_SERVER")

class Blockchain:

    def __init__(self) -> None:
        self.chain  = list()
        self.nodes = list()
        self.difficulty = 3
        genesis_block = self._create_block(
            index = 1,
            merkle_hash= "Genesis Block",
            proof = 1,
            previous_hash = "0",
        )
        self.chain.append(genesis_block)

    def update_nodes(self) -> None:
        try:
            urlGET = f"http://{COORDINATION_SERVER}/"
            self.nodes = requests.get(urlGET).json()['hosts']
        except:
            print("Unable to connect to Coordination Server.")

    def mine_block(self,data: dict) -> dict:
        merkle_hash = data["merkle_hash"]
        self.replace_chain()
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = len(self.chain) + 1
        proof = self._proof_of_work(previous_proof=previous_proof, index=index, data=merkle_hash, difficulty=self.difficulty)
        previous_hash =  self._hash(block=previous_block)
        block = self._create_block(
            merkle_hash=merkle_hash,
            proof=proof,
            previous_hash=previous_hash,
            index=index)
        self.chain.append(block)
        return block

    def _hash(self, block: dict) -> str:
        encoded_block = _json.dumps(block, sort_keys=True).encode()

        return _hashlib.sha256(encoded_block).hexdigest()

    def _to_digest(self,new_proof: int,previous_proof: int,index: int,data: str) -> bytes:
        to_digest = str(new_proof ** 4 - previous_proof ** 2 + index) + data

        return to_digest.encode()

    def _proof_of_work(self,previous_proof: int,index: int,data: str,difficulty: int) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof=new_proof, previous_proof=previous_proof, index=index, data=data)

            hash_value = _hashlib.sha256(to_digest).hexdigest()

            if hash_value[:difficulty] == "0" * difficulty:
                check_proof = True
            else:
                new_proof += 1

        return new_proof
    
    def get_previous_block(self) -> dict:
        return self.chain[-1]

    def _create_block(self, merkle_hash: str, proof: int, previous_hash: str, index: int) -> dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
            "merkle_hash": merkle_hash,
            "proof": proof,
            "previous_hash": previous_hash,
        }
        return block

    def is_chain_valid(self,chain: dict) -> bool:
        
        current_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            next_block = chain[block_index]

            if next_block["previous_hash"] != self._hash(current_block):
                return False
            
            current_proof = current_block["proof"]
            next_index,next_proof,next_merkle_hash = next_block["index"],next_block["proof"],next_block["merkle_hash"]
            hash_value = _hashlib.sha256(
                self._to_digest(
                    new_proof=next_proof,
                    previous_proof=current_proof, 
                    index=next_index,
                    data=next_merkle_hash
                )
            ).hexdigest()
            
            if hash_value[:self.difficulty] != "0" * self.difficulty:
                return False
            
            current_block = next_block
            block_index += 1

        return True
    
    def replace_chain(self) -> bool:
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            try:
                response = requests.get(f'http://{node}:8000/blockchain/get/')
            except:
                print(f"{node} is unavailable")
            if response.status_code == 200:
                chain = response.json()
                length = len(chain)
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False