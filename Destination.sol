// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("WARDEN");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR");

    // Test expects: wrapped_tokens(underlying) -> wrapped
    mapping(address => address) public wrapped_tokens;
    // Test expects: underlying_tokens(wrapped) -> underlying
    mapping(address => address) public underlying_tokens;
    
    address[] public tokens;

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    // Note: 'frm' is NOT indexed in the test file's event definition
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function createToken(address _underlying_token, string memory name, string memory symbol) public onlyRole(CREATOR_ROLE) returns(address) {
        BridgeToken newToken = new BridgeToken(_underlying_token, name, symbol, address(this));
        address wtoken = address(newToken);

        // Matching the test's mapping expectations
        wrapped_tokens[_underlying_token] = wtoken;
        underlying_tokens[wtoken] = _underlying_token;
        
        tokens.push(wtoken);

        emit Creation(_underlying_token, wtoken);
        return wtoken;
    }

    function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        address wtoken = wrapped_tokens[_underlying_token];
        require(wtoken != address(0), "Token not registered");

        BridgeToken(wtoken).mint(_recipient, _amount);

        emit Wrap(_underlying_token, wtoken, _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        address utoken = underlying_tokens[_wrapped_token];
        require(utoken != address(0), "Invalid wrapped token");

        BridgeToken(_wrapped_token).burnFrom(msg.sender, _amount);

        emit Unwrap(utoken, _wrapped_token, msg.sender, _recipient, _amount);
    }
}