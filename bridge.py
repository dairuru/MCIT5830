from eth_account.messages import encode_defunct

def scan_blocks(chain, contract_info="contract_info.json"):
    """
        Scan the last 5 blocks of the source/destination chains and trigger 
        the cross-chain counterpart function.
    """
    if chain not in ['source', 'destination']:
        print(f"Invalid chain: {chain}")
        return 0

    # 1. Setup Connections and Contracts
    w3_source = connect_to('source')
    w3_dest = connect_to('destination')
    
    source_data = get_contract_info('source', contract_info)
    dest_data = get_contract_info('destination', contract_info)
    
    # Load warden credentials (assuming key is in the source section or root of json)
    warden_key = source_data['warden_key'] 
    warden_account = w3_source.eth.account.from_key(warden_key)

    # Initialize Contract Objects
    source_contract = w3_source.eth.contract(address=source_data['address'], abi=source_data['abi'])
    dest_contract = w3_dest.eth.contract(address=dest_data['address'], abi=dest_data['abi'])

    # 2. Logic for Source -> Destination (Deposit -> Wrap)
    if chain == 'source':
        start_block = w3_source.eth.block_number - 5
        # Look for Deposit events
        event_filter = source_contract.events.Deposit.create_filter(fromBlock=start_block)
        events = event_filter.get_all_entries()

        for event in events:
            user = event.args.user
            amount = event.args.amount
            token = event.args.token
            
            # Create signature for the Destination's wrap function
            # Note: Ensure the message hashing matches your Solidity 'wrap' requirements
            message_hash = Web3.solidity_keccak(['address', 'uint256', 'address'], [user, amount, token])
            signature = w3_source.eth.account.sign_message(encode_defunct(hexstr=message_hash.hex()), private_key=warden_key)

            # Call wrap() on Destination (BSC)
            nonce = w3_dest.eth.get_transaction_count(warden_account.address)
            txn = dest_contract.functions.wrap(user, amount, token, signature.signature).build_transaction({
                'from': warden_account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3_dest.eth.gas_price
            })
            signed_txn = w3_dest.eth.account.sign_transaction(txn, warden_key)
            w3_dest.eth.send_raw_transaction(signed_txn.rawTransaction)

    # 3. Logic for Destination -> Source (Unwrap -> Withdraw)
    if chain == 'destination':
        start_block = w3_dest.eth.block_number - 5
        # Look for Unwrap events
        event_filter = dest_contract.events.Unwrap.create_filter(fromBlock=start_block)
        events = event_filter.get_all_entries()

        for event in events:
            user = event.args.user
            amount = event.args.amount
            token = event.args.token # This should be the original underlying token address
            
            # Create signature for the Source's withdraw function
            message_hash = Web3.solidity_keccak(['address', 'uint256', 'address'], [user, amount, token])
            signature = w3_dest.eth.account.sign_message(encode_defunct(hexstr=message_hash.hex()), private_key=warden_key)

            # Call withdraw() on Source (AVAX)
            nonce = w3_source.eth.get_transaction_count(warden_account.address)
            txn = source_contract.functions.withdraw(user, amount, token, signature.signature).build_transaction({
                'from': warden_account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3_source.eth.gas_price
            })
            signed_txn = w3_source.eth.account.sign_transaction(txn, warden_key)
            w3_source.eth.send_raw_transaction(signed_txn.rawTransaction)