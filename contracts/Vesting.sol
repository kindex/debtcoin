// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "OpenZeppelin/openzeppelin-contracts@4.8.3/contracts/token/ERC20/IERC20.sol";

/// @title Debtcoin vesting contract
/// @author Andrey Pelipenko KindeX
/// @dev Contract is used for locking some amount of tokens for time period for target account.
///      Only target account can claim locked tokens after time period is passed.
///      Tokens can be locked only once.
///      Max vesting time is 183 days (half of a year).
contract Vesting {
    IERC20 debtcoin;

    /// @dev Vesting unlock timestamp
    uint public unlockTimestamp;
    /// @dev Amount of locked tokens
    uint public lockedValue;
    /// @dev Account, than can claim locked tokens
    address public targetAccount;

    event Locked(address account, uint value, uint unlockTimestamp);
    event Claimed(address account, uint value);

    constructor(IERC20 _debtcoin) {
        debtcoin = _debtcoin;
    }

    /// @dev Start vesting for target account
    ///      Do not forget to approve corresponding token amount for vesting contract as spender.
    function lock(address target, uint tokenAmount, uint timeDurationSeconds) external {
        require(timeDurationSeconds < 183 days, 'Duration too long');
        require(unlockTimestamp == 0, 'Vesting already was started');

        uint amountToSend = tokenAmount;
        unlockTimestamp = block.timestamp + timeDurationSeconds;
        lockedValue = tokenAmount;
        targetAccount = target;
        emit Locked(targetAccount, lockedValue, unlockTimestamp);

        debtcoin.transferFrom(msg.sender, address(this), amountToSend);
    }

    /// @dev Target contract can call claim after vesting unlock is over.
    function claim() external {
        require(msg.sender == targetAccount, 'Access denied');
        require(unlockTimestamp <= block.timestamp, 'Locked by time');
        require(lockedValue > 0, 'Empty balance');

        uint amountToSend = lockedValue;
        emit Claimed(targetAccount, lockedValue);
        lockedValue = 0;
        debtcoin.transfer(targetAccount, amountToSend);
    }
}
