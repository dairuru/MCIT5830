#!/bin/python
import hashlib
import os
import random

def mine_block(k, prev_hash, transactions):
    """
    k - Number of trailing zeros in the binary representation (integer)
    prev_hash - the hash of the previous block (bytes)
    transactions - a list of strings representing transactions
    """
    if not isinstance(k, int) or k < 0:
        print("mine_block expects positive integer")
        return b'\x00'

    # 1. Pre-prepare the base hash object with prev_hash and all transactions
    # This saves time by not re-hashing the same static data every loop
    base_m = hashlib.sha256()
    base_m.update(prev_hash)
    for line in transactions:
        base_m.update(line.encode('utf-8'))

    # 2. Brute-force the nonce
    nonce_counter = 0
    
    while True:
        # Create a copy of the base hash to add the current nonce
        m = base_m.copy()
        
        # Convert counter to string then to bytes
        nonce = str(nonce_counter).encode('utf-8')
        m.update(nonce)
        
        # Get the digest as bytes
        digest = m.digest()
        
        # 3. Check for k trailing zeros
        # Convert the hash bytes to a large integer
        # 'big' or 'little' endian doesn't matter as long as we are consistent
        hash_int = int.from_bytes(digest, byteorder='big')
        
        # A number has k trailing zeros if it is divisible by 2^k
        # We use the bitwise AND operator to check the last k bits
        if (hash_int & ((1 << k) - 1)) == 0:
            assert isinstance(nonce, bytes), 'nonce should be of type bytes'
            return nonce
        
        nonce_counter += 1

def get_random_lines(filename, quantity):
    """
    Helper function to get a list of 'transactions'
    """
    lines = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                lines.append(line.strip())
    except FileNotFoundError:
        # Fallback for local testing if file is missing
        return ["Transaction " + str(i) for i in range(quantity)]

    random_lines = []
    # Note: Using random.sample or ensuring the range is valid
    limit = min(len(lines), quantity)
    for x in range(limit):
        random_lines.append(random.choice(lines))
    return random_lines

if __name__ == '__main__':
    # Initial setup for testing
    filename = "bitcoin_text.txt"
    num_lines = 10 
    diff = 15 # Started with 15 for faster local testing
    
    # Mock previous hash (32 bytes)
    prev_hash = os.urandom(32)
    
    transactions = get_random_lines(filename, num_lines)
    
    print(f"Mining block with difficulty {diff}...")
    nonce = mine_block(diff, prev_hash, transactions)
    print(f"Success! Found Nonce: {nonce}")