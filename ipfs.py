import requests
import json
import os

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI0YTNjMzNmMC04OGVlLTQzY2EtYTAwNS05NzdlZDJkMmM4ZWYiLCJlbWFpbCI6ImRhaXJ1cnUxMDMwQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6IkZSQTEifSx7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6Ik5ZQzEifV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiIzNmZjY2FkMDRiYTU4NzY1NzFiNyIsInNjb3BlZEtleVNlY3JldCI6ImVkYzRiNThjYzhiMmYyOTNkYTE2MmY2YTFkMDc0MWQ5ZWNkYWE4MTgyYWM4ZDZiYWE5ZGI3NjE3NDAyYjA2ODYiLCJleHAiOjE4MDQwMzUyMTd9.YQQt7lTA00SBmrnFtm7ooqGbuVNICk6hc5Ru8barMfU"
PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
GATEWAYS = ["https://gateway.pinata.cloud/ipfs/","https://ipfs.io/ipfs/","https://cloudflare-ipfs.com/ipfs/"]

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	if not PINATA_JWT or PINATA_JWT == "PASTE_YOUR_PINATA_JWT_HERE":
		raise RuntimeError(
			"Missing Pinata JWT. Paste it into PINATA_JWT or set env var PINATA_JWT."
		)

	headers = {
		"Authorization": f"Bearer {PINATA_JWT}",
		"Content-Type": "application/json",
		}

	payload = {"pinataContent": data}

	resp = requests.post(PIN_JSON_URL, headers=headers, data=json.dumps(payload), timeout=30)
	resp.raise_for_status()
	j = resp.json()

	# Pinata typically returns the CID in the 'IpfsHash' field
	cid = j.get("IpfsHash")
	if not cid:
		raise RuntimeError(f"Unexpected Pinata response (missing IpfsHash): {j}")

	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	path = cid.strip()
	if path.startswith("ipfs://"):
		path = path[len("ipfs://") :]
	if path.startswith("/ipfs/"):
		path = path[len("/ipfs/") :]

	last_err = None
	for gw in GATEWAYS:
		url = gw + path
		try:
			r = requests.get(url, timeout=30)
			r.raise_for_status()

			if content_type == "json":
				data = r.json()
			else:
				data = json.loads(r.text)
			assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
