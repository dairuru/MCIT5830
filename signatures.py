from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import eth_account

def sign(m):
    w3 = Web3()

    # 1. Create a new Ethereum account
    account_object = Account.create()
    public_key = account_object.address
    private_key = account_object.key

    # 2. Encode the message according to Ethereum's signing standards
    # This adds the "\x19Ethereum Signed Message:\n" prefix
    message_encoded = encode_defunct(text=m)
    
    # 3. Sign the encoded message using the private key
    signed_message = Account.sign_message(message_encoded, private_key=private_key)

    print('Account created:\n'
          f'private key={w3.to_hex(private_key)}\naccount={public_key}\n')
    
    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)
    
    return public_key, signed_message


def verify(m, public_key, signed_message):
    # 1. Re-encode the original message to check against the signature
    message_encoded = encode_defunct(text=m)
    
    try:
        # 2. Recover the address that signed this message
        # .recover_message returns the Ethereum address (e.g., 0x123...)
        signer_address = Account.recover_message(message_encoded, signature=signed_message.signature)
        
        # 3. Check if the recovered address matches the provided public_key
        valid_signature = (signer_address.lower() == public_key.lower())
    except Exception:
        # If the signature format is mangled, it won't verify
        valid_signature = False

    assert isinstance(valid_signature, bool), "verify should return a boolean value"
    return valid_signature


if __name__ == "__main__":
    import random
    import string

    for i in range(10):
        # Generate a random 20-character string
        m = "".join([random.choice(string.ascii_letters) for _ in range(20)])

        pub_key, signature = sign(m)

        # Modifies every other message so that the signature fails to verify
        if i % 2 == 0:
            m = m + 'a'

        if verify(m, pub_key, signature):
            print(f"Iteration {i}: Signed Message Verified")
        else:
            print(f"Iteration {i}: Signed Message Failed to Verify")