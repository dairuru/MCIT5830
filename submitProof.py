import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from eth_account.messages import encode_defunct
from web3.middleware import ExtraDataToPOAMiddleware

# --- 1. Top-level functions (The grader looks for these) ---

def generate_primes(num_primes):
    primes_list = []
    num = 2
    while len(primes_list) < num_primes:
        for i in range(2, int(num**0.5) + 1):
            if (num % i) == 0:
                break
        else:
            primes_list.append(num)
        num += 1
    return primes_list

def convert_leaves(primes_list):
    return [int.to_bytes(p, 32, 'big') for p in primes_list]

def build_merkle(leaves):
    tree = [leaves]
    current_layer = leaves
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            node_a = current_layer[i]
            node_b = current_layer[i+1] if i+1 < len(current_layer) else current_layer[i]
            next_layer.append(hash_pair(node_a, node_b))
        tree.append(next_layer)
        current_layer = next_layer
    return tree

def prove_merkle(merkle_tree, random_indx):
    merkle_proof = []
    index = random_indx
    for i in range(len(merkle_tree) - 1):
        layer = merkle_tree[i]
        sibling_index = index + 1 if index % 2 == 0 else index - 1
        if sibling_index < len(layer):
            merkle_proof.append(layer[sibling_index])
        else:
            merkle_proof.append(layer[index])
        index //= 2
    return merkle_proof

# --- 2. Assignment logic and Signing ---

def sign_challenge(challenge):
    acct = get_account()
    message = encode_defunct(text=challenge)
    eth_sig_obj = eth_account.Account.sign_message(message, private_key=acct.key)
    return acct.address, eth_sig_obj.signature.hex()

def merkle_assignment():
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)
    leaves = convert_leaves(primes)
    tree = build_merkle(leaves)
    
    # We use a high index to avoid primes already claimed by others
    random_leaf_index = random.randint(1000, 8191) 
    proof = prove_merkle(tree, random_leaf_index)
    
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    addr, sig = sign_challenge(challenge)
    
    if sign_challenge_verify(challenge, addr, sig):
        print("Ready for submission.")
        # tx_hash = send_signed_msg(proof, leaves[random_leaf_index])

# --- 3. Existing Helper Functions (Keep these as they were) ---

def hash_pair(a, b):
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])

# ... rest of your helper functions (get_account, connect_to, etc.) ...

if __name__ == "__main__":
    merkle_assignment()