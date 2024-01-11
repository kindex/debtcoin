// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./Vesting.sol";

/// @title Debtcoin debug vesting contract
/// @author Andrey Pelipenko KindeX
/// @dev Contract is used for Vesting contract manual testing.
///      Lock duration is decreased to 1 hour.
contract VestingDebug is Vesting {

    constructor(IERC20 _debtcoin, address _owner, address _targetAccount)
        Vesting(_debtcoin, _owner, _targetAccount)
    {
        LOCK_DURATION = 60 minutes;
    }

}
