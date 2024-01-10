import pytest
import time


@pytest.fixture
def debtcoin(deployer, Debtcoin, holder):
    result = deployer.deploy(Debtcoin, holder)
    yield result

@pytest.fixture
def vesting(deployer, Vesting, debtcoin, targetAccount):
    result = deployer.deploy(Vesting, debtcoin, targetAccount)
    yield result

