from eth_account.messages import encode_defunct

def scan_blocks(chain, contract_info="contract_info.json"):
    if chain not in ['source', 'destination']:
        return 0

    w3_source = connect_to('source')
    w3_dest = connect_to('destination')
    
    # Load data from JSON
    source_data = get_contract_info('source', contract_info)
    dest_data = get_contract_info('destination', contract_info)
    
    # IMPORTANT: Ensure 'warden_key' is added to your contract_info.json
    warden_key = source_data['warden_key'] 
    warden_account = w3_source.eth.account.from_key(warden_key)

    source_contract = w3_source.eth.contract(address=source_data['address'], abi=source_data['abi'])
    dest_contract = w3_dest.eth.contract(address=dest_data['address'], abi=dest_data['abi'])

    # --- Source -> Destination (Deposit -> Wrap) ---
    if chain == 'source':
        start_block = w3_source.eth.block_number - 5
        event_filter = source_contract.events.Deposit.create_filter(fromBlock=start_block)
        for event in event_filter.get_all_entries():
            # Based on your ABI: args are 'recipient', 'amount', 'token'
            user = event.args.recipient
            amount = event.args.amount
            token = event.args.token
            
            # Call wrap() on Destination
            nonce = w3_dest.eth.get_transaction_count(warden_account.address)
            txn = dest_contract.functions.wrap(token, user, amount).build_transaction({
                'from': warden_account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3_dest.eth.gas_price
            })
            signed_txn = w3_dest.eth.account.sign_transaction(txn, warden_key)
            w3_dest.eth.send_raw_transaction(signed_txn.rawTransaction)

    # --- Destination -> Source (Unwrap -> Withdraw) ---
    if chain == 'destination':
        start_block = w3_dest.eth.block_number - 5
        event_filter = dest_contract.events.Unwrap.create_filter(fromBlock=start_block)
        for event in event_filter.get_all_entries():
            # Based on your ABI: args are 'to', 'amount', 'underlying_token'
            user = event.args.to
            amount = event.args.amount
            token = event.args.underlying_token
            
            # Call withdraw() on Source
            nonce = w3_source.eth.get_transaction_count(warden_account.address)
            txn = source_contract.functions.withdraw(token, user, amount).build_transaction({
                'from': warden_account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3_source.eth.gas_price
            })
            signed_txn = w3_source.eth.account.sign_transaction(txn, warden_key)
            w3_source.eth.send_raw_transaction(signed_txn.rawTransaction)