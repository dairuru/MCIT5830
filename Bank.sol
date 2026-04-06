// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC777/ERC777.sol";
import "@openzeppelin/contracts/token/ERC777/IERC777Recipient.sol";
import "@openzeppelin/contracts/interfaces/IERC1820Registry.sol";
import "./MCITR.sol";

contract Bank is AccessControl, IERC777Recipient {
    MCITR public token;
    
    // Official EIP1820 Registry address
    IERC1820Registry private _erc1820 = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24);
    bytes32 constant private TOKENS_RECIPIENT_INTERFACE_HASH = keccak256("ERC777TokensRecipient");

    event Deposit(address indexed depositor, uint256 amount);
    event Claim(address indexed withdrawer, uint256 amount);
    event Withdrawal(address indexed withdrawer, uint256 amount);

    mapping(address => uint256) public balances;
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public withdrawals;

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        // Initialize the ERC777 token
        token = new MCITR(0, address(this)); 
        // Register the Bank itself to be able to receive its own tokens during 'redeem'
        _erc1820.setInterfaceImplementer(address(this), TOKENS_RECIPIENT_INTERFACE_HASH, address(this));
    }

    function deposit() public payable {
        uint256 amount = msg.value;
        require(amount > 0, "Deposit must be > 0");
        balances[msg.sender] += amount;
        deposits[msg.sender] += amount;
        emit Deposit(msg.sender, amount);
    }

    /* VULNERABLE FUNCTION: The reentrancy happens here */
    function claimAll() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, 'Cannot withdraw 0');

        emit Claim(msg.sender, amount);
        
        // ERC777 Minting triggers tokensReceived() on the recipient (the Attacker)
        // because the balance is not yet 0, the Attacker can call claimAll again!
        token.mint(msg.sender, amount); 

        balances[msg.sender] = 0;
        withdrawals[msg.sender] += amount;
    }

    function redeem(uint256 amount) public {
        // Pull tokens from user (requires 'approve' or 'operator' status)
        token.transferFrom(msg.sender, address(this), amount);
        
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
        
        emit Withdrawal(msg.sender, amount);
    }

    function tokensReceived(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes calldata userData,
        bytes calldata operatorData
    ) external view override {
        require(msg.sender == address(token), "Invalid token");
    }

    // Fallback to receive ETH
    receive() external payable {}
}
