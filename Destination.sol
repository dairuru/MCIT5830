// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
	mapping( address => address) public underlying_tokens;
	mapping( address => address) public wrapped_tokens;
	address[] public tokens;

	event Creation( address indexed underlying_token, address indexed wrapped_token );
	event Wrap( address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount );
	event Unwrap( address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

	function wrap(address _underlying_token, address _recipient, uint256 _amount ) public onlyRole(WARDEN_ROLE) {
        //YOUR CODE HERE
        // 1. Lookup the corresponding BridgeToken
        address wrappedToken = underlying_to_wrapped[_underlying_token];
        
        // 2. Ensure the underlying asset has been registered via createToken
        require(wrappedToken != address(0), "Destination: underlying asset not registered");

        // 3. Mint the tokens to the recipient
        BridgeToken(wrappedToken).mint(_recipient, _amount);

        // 4. Emit the Wrap event
        emit Wrap(_underlying_token, wrappedToken, _recipient, _amount);
	}

	function unwrap(address _wrapped_token, address _recipient, uint256 _amount ) public {
		//YOUR CODE HERE
        // 1. Identify the underlying asset for event logging
        address underlyingToken = wrapped_to_underlying[_wrapped_token];
        require(underlyingToken != address(0), "Destination: invalid wrapped token");

        // 2. Burn the tokens from the user's balance
        // This requires BridgeToken to have a burn function that the Destination can call.
        // Usually, this is BridgeToken.burnFrom(msg.sender, _amount)
        BridgeToken(_wrapped_token).burnFrom(msg.sender, _amount);

        // 3. Emit the Unwrap event
        emit Unwrap(underlyingToken, _wrapped_token, msg.sender, _recipient, _amount);
	}

	function createToken(address _underlying_token, string memory name, string memory symbol ) public onlyRole(CREATOR_ROLE) returns(address) {
        //YOUR CODE HERE
        // 1. Deploy the new BridgeToken contract
        // BridgeToken constructor expects (underlying, name, symbol)
        BridgeToken newToken = new BridgeToken(_underlying_token, name, symbol);
        address wrappedAddress = address(newToken);

        // 2. Register the token in our mappings
        underlying_to_wrapped[_underlying_token] = wrappedAddress;
        wrapped_to_underlying[wrappedAddress] = _underlying_token;
        
        // 3. Track the token address
        tokens.push(wrappedAddress);

        // 4. Emit the Creation event
        emit Creation(_underlying_token, wrappedAddress);

        return wrappedAddress;
	}

}


