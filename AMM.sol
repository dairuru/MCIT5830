// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract AMM is AccessControl {
    bytes32 public constant LP_ROLE = keccak256("LP_ROLE");
    uint256 public invariant;
    address public tokenA;
    address public tokenB;
    uint256 feebps = 3; // 0.03% fee

    event Swap(address indexed _inToken, address indexed _outToken, uint256 inAmt, uint256 outAmt);
    event LiquidityProvision(address indexed _from, uint256 AQty, uint256 BQty);
    event Withdrawal(address indexed _from, address indexed recipient, uint256 AQty, uint256 BQty);

    constructor(address _tokenA, address _tokenB) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(LP_ROLE, msg.sender);
        require(_tokenA != address(0) && _tokenB != address(0), 'Token address cannot be 0');
        require(_tokenA != _tokenB, 'Tokens cannot be the same');
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    function tradeTokens(address sellToken, uint256 sellAmount) public {
        require(sellToken == tokenA || sellToken == tokenB, 'Invalid token');
        require(sellAmount > 0, 'Cannot trade 0');
        require(invariant > 0, 'No liquidity');

        address buyToken = (sellToken == tokenA) ? tokenB : tokenA;
        uint256 resIn = ERC20(sellToken).balanceOf(address(this));
        uint256 resOut = ERC20(buyToken).balanceOf(address(this));

        // Calculate amount after fee: sellAmount * (1 - 3/10000)
        uint256 sellAmountWithFee = (sellAmount * (10000 - feebps)) / 10000;
        
        // Constant Product Formula: (resIn + sellAmtWithFee) * (resOut - buyAmt) = invariant
        // buyAmt = resOut - (invariant / (resIn + sellAmtWithFee))
        uint256 buyAmount = resOut - (invariant / (resIn + sellAmountWithFee));

        require(buyAmount > 0, 'Insufficient output amount');
        require(buyAmount < resOut, 'Insufficient liquidity');

        ERC20(sellToken).transferFrom(msg.sender, address(this), sellAmount);
        ERC20(buyToken).transfer(msg.sender, buyAmount);

        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        emit Swap(sellToken, buyToken, sellAmount, buyAmount);
    }

    function provideLiquidity(uint256 amtA, uint256 amtB) public {
        require(amtA > 0 && amtB > 0, 'Must provide both tokens');
        
        ERC20(tokenA).transferFrom(msg.sender, address(this), amtA);
        ERC20(tokenB).transferFrom(msg.sender, address(this), amtB);

        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        emit LiquidityProvision(msg.sender, amtA, amtB);
    }

    function withdrawLiquidity(address recipient, uint256 amtA, uint256 amtB) public onlyRole(LP_ROLE) {
        require(amtA > 0 || amtB > 0, 'Cannot withdraw 0');
        require(recipient != address(0), 'Cannot withdraw to 0 address');

        if(amtA > 0) ERC20(tokenA).transfer(recipient, amtA);
        if(amtB > 0) ERC20(tokenB).transfer(recipient, amtB);

        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        emit Withdrawal(msg.sender, recipient, amtA, amtB);
    }

    function getTokenAddress(uint256 index) public view returns(address) {
        return (index == 0) ? tokenA : tokenB;
    }
}
