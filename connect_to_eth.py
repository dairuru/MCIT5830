import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.providers.rpc import HTTPProvider

'''
If you use one of the suggested infrastructure providers, the url will be of the form
now_url  = f"https://eth.nownodes.io/{now_token}"
alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
'''


def connect_to_eth():
	url = f"https://eth-mainnet.alchemyapi.io/v2/q32XCLf5tg3sd0mWojqa6"
	w3 = Web3(HTTPProvider(url))
	assert w3.is_connected(), f"Failed to connect to provider at {url}"
	return w3


def connect_with_middleware(contract_json):
	with open(contract_json, "r") as f:
		d = json.load(f)
		bsc = d['bsc']
		address = d['address']
		abi = d['abi']

	# connect to BSC testnet/mainnet RPC (default to a known BSC testnet seed)
	bnb_url = f"https://bnb-testnet.g.alchemy.com/v2/q32XCLf5tg3sd0mWojqa6"
	w3 = Web3(HTTPProvider(bnb_url))
	assert w3.is_connected(), f"Failed to connect to provider at {bnb_url}"

	# inject POA middleware required by BSC-style chains
	w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
	contract = w3.eth.contract(address=address, abi=abi)
	return w3, contract


if __name__ == "__main__":
	connect_to_eth()
