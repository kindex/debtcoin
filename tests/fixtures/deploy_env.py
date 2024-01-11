import pytest
import time


@pytest.fixture
def debtcoin(deployer, Debtcoin, holder):
    result = deployer.deploy(Debtcoin, holder)
    yield result

@pytest.fixture
def vesting(deployer, Vesting, debtcoin, targetAccount, owner):
    result = deployer.deploy(Vesting, debtcoin, owner, targetAccount)
    yield result

