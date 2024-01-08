import logging
import time
from brownie import Wei, reverts

LOGGER = logging.getLogger(__name__)

def test_happy_path(chain, holder, targetAccount, debtcoin, vesting):
    LOCK_DURATION = 100*60

    assert debtcoin.balanceOf(holder) == 32_000_000_00, "initial balance"
    assert debtcoin.balanceOf(targetAccount) == 0, "initial balance"

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    tx = vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})

    e = tx.events[0]
    assert e.name == 'Locked', tx.events
    assert e['account'] == targetAccount, e
    assert e['value'] == 2_000_000_00, e

    assert debtcoin.balanceOf(holder) == 30_000_000_00, "balance after lock"
    assert debtcoin.balanceOf(targetAccount) == 0, "balance after lock"

    chain.sleep(LOCK_DURATION)
    chain.mine()

    tx = vesting.claim({'from':targetAccount})

    e = tx.events[0]
    assert e.name == 'Claimed', tx.events
    assert e['account'] == targetAccount, e
    assert e['value'] == 2_000_000_00, e

    assert debtcoin.balanceOf(holder) == 30_000_000_00, "balance after claim"
    assert debtcoin.balanceOf(targetAccount) == 2_000_000_00, "balance after claim"


def test_claim_checks(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = 100*60

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})

    with reverts("Locked by time"):
        vesting.claim({'from':targetAccount})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    with reverts("Access denied"):
        vesting.claim({'from':holder})

    with reverts("Access denied"):
        vesting.claim({'from':accounts[5]})

    vesting.claim({'from':targetAccount})

    with reverts("Empty balance"):
        vesting.claim({'from':targetAccount})


def test_lock_checks(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = 100*60

    with reverts("ERC20: insufficient allowance"):
        vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})

    with reverts("ERC20: insufficient allowance"):
        vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':accounts[5]})

    with reverts("Duration too long"):
        vesting.lock(targetAccount, 2_000_000_00, 24*60*60*365, {'from':accounts[5]})

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})

    with reverts("Vesting already was started"):
        vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    vesting.claim({'from':targetAccount})

    with reverts("Vesting already was started"):
        vesting.lock(targetAccount, 2_000_000_00, LOCK_DURATION, {'from':holder})
