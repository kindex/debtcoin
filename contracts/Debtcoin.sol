// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "OpenZeppelin/openzeppelin-contracts@4.8.3/contracts/token/ERC20/ERC20.sol";

/// @title Debtcoin ERC20 token
/// @author Andrey Pelipenko KindeX
/// @dev Mints tokens on contracts deploy process.
///      Mint and burn are not allowed after that.
contract Debtcoin is ERC20 {

    uint constant initialMint = 32_000_000;

    constructor(address holder) ERC20("Debtcoin", "DBT") {
        _mint(holder, initialMint * (10 ** decimals()));
    }

    function decimals() public view virtual override returns (uint8) {
        return 2;
    }
}
