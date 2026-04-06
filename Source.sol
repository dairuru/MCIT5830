// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");

    mapping(address => bool) public approved;
    address[] public tokens;

    event Deposit(
        address indexed token,
        address indexed recipient,
        uint256 amount
    );
    event Withdrawal(
        address indexed token,
        address indexed recipient,
        uint256 amount
    );
    event Registration(address indexed token);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function deposit(address _token, address _recipient, uint256 _amount) public {
        // 1. Check if the token being deposited has been “registered”
        require(approved[_token], "Token not registered");
        require(_amount > 0, "Amount must be greater than 0");

        // 2. Use the ERC20 “transferFrom” function to pull tokens into the deposit contract
        // Note: The user must call 'approve' on the ERC20 contract first
        bool success = IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        require(success, "Transfer failed");

        // 3. Emit a “Deposit” event
        emit Deposit(_token, _recipient, _amount);
    }

    function withdraw(address _token, address _recipient, uint256 _amount) 
        public 
        onlyRole(WARDEN_ROLE) 
    {
        require(_recipient != address(0), "Invalid recipient");
        require(_amount > 0, "Amount must be greater than 0");

        // 1. Push the tokens to the recipient using the ERC20 “transfer” function
        bool success = IERC20(_token).transfer(_recipient, _amount);
        require(success, "Transfer failed");

        // 2. Emit a Withdrawal event
        emit Withdrawal(_token, _recipient, _amount);
    }

    function registerToken(address _token) 
        public 
        onlyRole(ADMIN_ROLE) 
    {
        // 1. Check that the token has not already been registered
        require(_token != address(0), "Invalid token address");
        require(!approved[_token], "Token already registered");

        // 2. Add the token address to the list of registered tokens
        approved[_token] = true;
        tokens.push(_token);

        // 3. Emit a Registration event
        emit Registration(_token);
    }
}
