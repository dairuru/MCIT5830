from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account
import eth_account
import os

def sign_message(challenge, filename="secret_key.txt"):
    """
    challenge - byte string
    filename - filename of the file that contains your account secret key
    """
    # 1. Read the private key from your local file
    with open(filename, "r") as f:
        # .strip() removes any accidental whitespace or newlines
        key = f.read().strip() 
        
    assert(len(key) > 0), "Your account secret_key.txt is empty"

    # 2. Reconstruct the account object from the private key
    # This allows us to access both the address and the signing capability
    account = Account.from_key(key)
    eth_addr = account.address

    # 3. Encode the challenge (byte string) for EIP-191 compliance
    message = encode_defunct(primitive=challenge)

    # 4. Sign the message
    signed_message = Account.sign_message(message, private_key=key)

    # Verification check provided in your skeleton
    assert eth_account.Account.recover_message(message, signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"

    # Return the signature object and the address
    return signed_message, eth_addr

if __name__ == "__main__":
    # Note: Before running this, ensure "secret_key.txt" exists 
    # and contains your 0x... hex private key.
    try:
        for i in range(4):
            challenge = os.urandom(64)
            sig, addr = sign_message(challenge=challenge)
            print(f"Iteration {i} - Address: {addr}")
    except FileNotFoundError:
        print("Error: Please create a 'secret_key.txt' file with your private key first.")