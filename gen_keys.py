from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account
import eth_account
import os

def sign_message(challenge, filename="secret_key.txt"):
    """
    challenge - byte string
    filename - filename of the file that contains your account secret key
    To pass the tests, your signature must verify, and the account you use
    must have testnet funds on both the bsc and avalanche test networks.
    """
    # Read the private key from your local file
    with open(filename, "r") as f:
        # .strip() handles any leading/trailing whitespace or newlines
        key = f.read().strip()
        
    assert(len(key) > 0), "Your account secret_key.txt is empty"

    w3 = Web3()
    
    # 1. Encode the message/challenge according to EIP-191
    message = encode_defunct(challenge)

    # 2. Recover the account from the private key
    # This derives the public address (eth_addr) from the private key
    account = Account.from_key(key)
    eth_addr = account.address

    # 3. Sign the encoded message using the private key
    signed_message = Account.sign_message(message, private_key=key)

    # The skeleton's built-in check
    assert eth_account.Account.recover_message(message, signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"

    # Return the SignedMessage object and the address string
    return signed_message, eth_addr


if __name__ == "__main__":
    # Ensure you have created secret_key.txt in this folder with your 0x... key!
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = sign_message(challenge=challenge)
        print(f"Address: {addr}")