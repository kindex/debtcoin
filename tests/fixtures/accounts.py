import pytest

@pytest.fixture
def deployer(accounts):
    yield accounts[0]

@pytest.fixture
def holder(accounts):
    yield accounts[1]

@pytest.fixture
def targetAccount(accounts):
    yield accounts[2]

