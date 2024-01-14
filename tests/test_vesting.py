import logging
import time
from brownie import Wei, reverts

LOGGER = logging.getLogger(__name__)

def test_happy_path(chain, holder, targetAccount, debtcoin, vesting):
    LOCK_DURATION = vesting.LOCK_DURATION()

    assert debtcoin.balanceOf(holder) == 32_000_000_00, "initial balance"
    assert debtcoin.balanceOf(targetAccount) == 0, "initial balance"
    assert debtcoin.balanceOf(vesting) == 0, "initial balance"

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    tx = vesting.lock(2_000_000_00, {'from':holder})

    e = tx.events[0]
    assert e.name == 'Locked', tx.events
    assert e['value'] == 2_000_000_00, e

    assert debtcoin.balanceOf(holder) == 30_000_000_00, "balance after lock"
    assert debtcoin.balanceOf(targetAccount) == 0, "balance after lock"
    assert debtcoin.balanceOf(vesting) == 2_000_000_00, "initial balance"

    chain.sleep(LOCK_DURATION)
    chain.mine()

    tx = vesting.claim(2_000_000_00, {'from':targetAccount})

    e = tx.events[0]
    assert e.name == 'Claimed', tx.events
    assert e['account'] == targetAccount, e
    assert e['value'] == 2_000_000_00, e

    assert debtcoin.balanceOf(holder) == 30_000_000_00, "balance after claim"
    assert debtcoin.balanceOf(targetAccount) == 2_000_000_00, "balance after claim"
    assert debtcoin.balanceOf(vesting) == 0, "initial balance"


def test_lock_checks(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = vesting.LOCK_DURATION()

    with reverts("ERC20: insufficient allowance"):
        vesting.lock(2_000_000_00, {'from':holder})

    with reverts("ERC20: insufficient allowance"):
        vesting.lock(2_000_000_00, {'from':accounts[5]})

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    vesting.lock(2_000_000_00, {'from':holder})

    # second lock
    vesting.lock(2_000_000_00, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    vesting.claim(2_000_000_00, {'from':targetAccount})

    # can lock after claim
    vesting.lock(2_000_000_00, {'from':holder})

def test_serial_lock(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = vesting.LOCK_DURATION()

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    with reverts("No unlocked tokens"):
        vesting.claim(1, {'from':targetAccount})

    chain.sleep(LOCK_DURATION - 4*100)
    chain.mine()

    with reverts("No unlocked tokens"):
        vesting.claim(1, {'from':targetAccount})

    chain.sleep(100)
    chain.mine()

    assert vesting.getUnlockedBalance() == 10


    vesting.claim(1, {'from':targetAccount})
    assert debtcoin.balanceOf(targetAccount) == 1, "balance after claim"

    assert vesting.getUnlockedBalance() == 9

    vesting.claim(8, {'from':targetAccount})
    assert debtcoin.balanceOf(targetAccount) == 9, "balance after claim"

    # can claim only 1
    tx = vesting.claim(2, {'from':targetAccount})
    e = tx.events[0]
    assert e.name == 'Claimed', tx.events
    assert e['value'] == 1, e

    assert debtcoin.balanceOf(targetAccount) == 10, "balance after claim"

    chain.sleep(200)
    chain.mine()

    assert vesting.getUnlockedBalance() == 20

    # claim 2 locks
    vesting.claim(15, {'from':targetAccount})
    assert debtcoin.balanceOf(targetAccount) == 25, "balance after claim"

    assert vesting.getUnlockedBalance() == 5

    chain.sleep(100)
    chain.mine()

    assert vesting.getUnlockedBalance() == 15

    tx = vesting.claim(16, {'from':targetAccount})
    e = tx.events[0]
    assert e.name == 'Claimed', tx.events
    assert e['value'] == 15, e
    assert debtcoin.balanceOf(targetAccount) == 40, "balance after claim"

def test_claim_checks(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = vesting.LOCK_DURATION()

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    vesting.lock(2_000_000_00, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    with reverts("Access denied"):
        vesting.claim(1, {'from':holder})

    with reverts("Access denied"):
        vesting.claim(1, {'from':accounts[5]})

    vesting.claim(1, {'from':targetAccount})


def test_change_address(chain, holder, targetAccount, debtcoin, vesting, accounts, deployer, owner):
    LOCK_DURATION = vesting.LOCK_DURATION()

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})
    vesting.lock(2_000_000_00, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    vesting.claim(1, {'from':targetAccount})
    vesting.setTargetAccount(accounts[5], {'from': owner})
    vesting.claim(2, {'from':accounts[5]})

    with reverts("Access denied"):
        vesting.claim(1, {'from':targetAccount})

    assert debtcoin.balanceOf(targetAccount) == 1, "after claim"
    assert debtcoin.balanceOf(accounts[5]) == 2, "after claim"


def test_access(chain, holder, targetAccount, debtcoin, vesting, accounts, deployer, owner):

    with reverts("Ownable: caller is not the owner"):
        vesting.setTargetAccount(accounts[5], {'from': accounts[5]})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': accounts[5]})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': holder})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': deployer})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': targetAccount})
    with reverts("Ownable: caller is not the owner"):
        vesting.withdrawERC20(debtcoin, {'from': targetAccount})

    vesting.transferOwnership(holder, {'from': owner})

    vesting.setTargetAccount(accounts[5], {'from': holder})

    with reverts("Ownable: caller is not the owner"):
        vesting.setTargetAccount(accounts[5], {'from': deployer})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': deployer})
    with reverts("Ownable: caller is not the owner"):
        vesting.transferOwnership(holder, {'from': owner})
    with reverts("Ownable: caller is not the owner"):
        vesting.withdrawERC20(debtcoin, {'from': owner})


def test_claim_all(chain, holder, targetAccount, debtcoin, vesting, accounts):
    LOCK_DURATION = vesting.LOCK_DURATION()

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    chain.sleep(100)
    chain.mine()

    vesting.lock(10, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    assert vesting.getUnlockedBalance() == 40

    vesting.claim(1, {'from':targetAccount})
    assert debtcoin.balanceOf(targetAccount) == 1, "balance after claim"

    assert vesting.getUnlockedBalance() == 39

    vesting.claimAll({'from':targetAccount})
    assert debtcoin.balanceOf(targetAccount) == 40, "balance after claim"

    assert vesting.getUnlockedBalance() == 0

def test_prod_settings(chain, holder, targetAccount, debtcoin, vesting, accounts):
    assert vesting.LOCK_DURATION() == 183*24*60*60, '183 days'

def test_withdraw(chain, holder, targetAccount, debtcoin, vesting, accounts, owner):
    LOCK_DURATION = vesting.LOCK_DURATION()

    debtcoin.approve(vesting, 32_000_000_00, {'from':holder})

    debtcoin.transfer(vesting, 3, {'from':holder})

    vesting.lock(10, {'from':holder})
    chain.sleep(100)
    chain.mine()
    vesting.lock(10, {'from':holder})

    assert debtcoin.balanceOf(owner) == 0, "balance before withdrawERC20"

    debtcoin.transfer(vesting, 4, {'from':holder})

    chain.sleep(LOCK_DURATION)
    chain.mine()

    vesting.withdrawERC20(debtcoin, {'from':owner})

    assert debtcoin.balanceOf(owner) == 7, "balance after withdrawERC20"

    assert vesting.getUnlockedBalance() == 20