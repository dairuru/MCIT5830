from eth_account import Account
import os

# 1. Generate a new, random Ethereum account
new_account = Account.create()

# 2. Extract the private key and address
private_key = new_account.key.hex()
address = new_account.address

# 3. Save the private key to secret_key.txt
with open("secret_key.txt", "w") as f:
    f.write(private_key)

print(f"Success! Account created.")
print(f"Address: {address}")
print(f"Private key saved to secret_key.txt")
print("-" * 30)
print("IMPORTANT: Copy the address above and use it with the faucets.")