// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "OpenZeppelin/openzeppelin-contracts@4.8.3/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.8.3/contracts/access/Ownable.sol";

/// @title Debtcoin vesting contract
/// @author Andrey Pelipenko KindeX
/// @dev Contract is used for locking some amount of tokens for time period for target account.
///      Only target account can claim locked tokens after time period is passed.
///      Tokens can be locked only once.
///      Max vesting time is 183 days (half of a year).
contract Vesting is Ownable {
    IERC20 debtcoin;

    uint constant public LOCK_DURATION = 183 days;

    struct LockedValue {
        /// @dev Amount of locked tokens
        uint lockedValue;
        /// @dev Vesting unlock timestamp
        uint unlockTimestamp;
    }

    LockedValue[] public lockedValues;

    /// @dev Account, than can claim locked tokens
    address public targetAccount;

    event Locked(uint value, uint unlockTimestamp);
    event Claimed(address account, uint value);

    constructor(IERC20 _debtcoin, address _targetAccount) {
        debtcoin = _debtcoin;
        targetAccount = _targetAccount;
    }

    /// @dev Start vesting for target account.
    ///      Do not forget to approve corresponding token amount for vesting contract as spender.
    ///      Anyone can start vesting.
    function lock(uint tokenAmount) external {
        uint unlockTimestamp = block.timestamp + LOCK_DURATION;
        lockedValues.push(LockedValue(tokenAmount, unlockTimestamp));
        emit Locked(tokenAmount, unlockTimestamp);

        debtcoin.transferFrom(msg.sender, address(this), tokenAmount);
    }

    /// @dev Target contract can call claim after vesting unlock is over.
    function claim(uint wantValue) external {
        require(msg.sender == targetAccount, 'Access denied');
        uint foundValue = 0;

        for (uint i = 0; i < lockedValues.length; i++) {
            LockedValue storage lv = lockedValues[i];
            if (lv.unlockTimestamp <= block.timestamp && lv.lockedValue > 0) {
                uint amountToSend;
                if (wantValue > lv.lockedValue) {
                    amountToSend = lv.lockedValue;
                    lv.lockedValue = 0;
                } else {
                    amountToSend = wantValue;
                    lv.lockedValue -= amountToSend;
                }
                wantValue -= amountToSend;
                foundValue += amountToSend;

                if (wantValue == 0) {
                    break;
                }
            }
        }
        require(foundValue > 0, "No unlocked tokens");
        emit Claimed(targetAccount, foundValue);
        debtcoin.transfer(targetAccount, foundValue);
    }

    function setTargetAccount(address newTargetAccount) external onlyOwner {
        targetAccount = newTargetAccount;
    }
}
