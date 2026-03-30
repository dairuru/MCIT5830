import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from eth_account.messages import encode_defunct
from web3.middleware import ExtraDataToPOAMiddleware

def merkle_assignment():
    """
    Main execution function to generate primes, build the tree, 
    and sign the challenge for the grader.
    """
    # 1. Generate the list of primes as integers
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    # 2. Create a version of the list of primes in bytes32 format
    leaves = convert_leaves(primes)

    # 3. Build a Merkle tree
    tree = build_merkle(leaves)

    # 4. Select a random leaf index (avoiding 0 as it's usually claimed)
    # 8192 primes means indices 0 to 8191
    random_leaf_index = random.randint(1, 8191) 
    proof = prove_merkle(tree, random_leaf_index)

    # 5. Sign the challenge for the autograder
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        print(f"Signature verified for {addr}")
        tx_hash = send_signed_msg(proof, leaves[random_leaf_index])
        print(f"Transaction sent! Hash: {tx_hash}")

def generate_primes(num_primes):
    """ Generates the first n prime numbers. """
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
    """ Converts integer primes to 32-byte big-endian format. """
    return [int.to_bytes(p, 32, 'big') for p in primes_list]

def build_merkle(leaves):
    """ 
    Builds the Merkle Tree. 
    Returns a list of layers, where tree[0] is the leaves and tree[-1] is the root.
    """
    tree = [leaves]
    current_layer = leaves
    
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            node_a = current_layer[i]
            # Since we have 8192 leaves (power of 2), we will always have pairs
            node_b = current_layer[i+1] if i+1 < len(current_layer) else current_layer[i]
            next_layer.append(hash_pair(node_a, node_b))
        tree.append(next_layer)
        current_layer = next_layer
    return tree

def prove_merkle(merkle_tree, random_indx):
    """ Generates the Merkle proof (sibling hashes) for a leaf index. """
    merkle_proof = []
    index = random_indx
    
    for i in range(len(merkle_tree) - 1):
        layer = merkle_tree[i]
        # XOR with 1 finds the sibling (0->1, 1->0, 2->3, 3->2)
        sibling_index = index ^ 1
        
        if sibling_index < len(layer):
            merkle_proof.append(layer[sibling_index])
        else:
            merkle_proof.append(layer[index])
            
        index //= 2
    return merkle_proof

def sign_challenge(challenge):
    """
    Takes a challenge (string)
    Returns address, sig (in hex)
    """
    acct = get_account()
    addr = acct.address

    message = encode_defunct(text=challenge)

    signed = eth_account.Account.sign_message(message, private_key=acct.key)

    if hasattr(signed, "signature"):
        sig = signed.signature.hex()
    else:
        sig = signed

    return addr, sig

def send_signed_msg(proof, random_leaf):
    """ Sends the transaction to the blockchain contract. """
    chain = 'bsc'
    acct = get_account()
    address, abi = get_contract_info(chain)
    w3 = connect_to(chain)

    contract = w3.eth.contract(address=address, abi=abi)
    
    tx = contract.functions.submit(proof, random_leaf).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('10', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return tx_hash.hex()

# --- Helper Functions ---

def hash_pair(a, b):
    """ Hashes two nodes after sorting them (OpenZeppelin standard). """
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])

def connect_to(chain):
    if chain not in ['avax','bsc']: return None
    api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/" if chain == 'bsc' else "https://api.avax-test.network/ext/bc/C/rpc"
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3

def get_account():
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().rstrip()
    if sk.startswith("0x"): sk = sk[2:]
    return eth_account.Account.from_key(sk)

def get_contract_info(chain):
    # Robust path finding for Codio
    cur_dir = Path(__file__).parent.absolute()
    contract_file = cur_dir / "contract_info.json"
    if not contract_file.is_file():
        contract_file = Path("contract_info.json")
    
    with open(contract_file, "r") as f:
        d = json.load(f)[chain]
    return d['address'], d['abi']

def sign_challenge_verify(challenge, addr, sig):
    message = encode_defunct(text=challenge)
    recovered_addr = eth_account.Account.recover_message(message, signature=sig)
    return recovered_addr == addr

if __name__ == "__main__":
    merkle_assignment()