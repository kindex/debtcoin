import os
from brownie import *

PUBLISH_SOURCES=True

private_key=os.getenv('DEBTCOIN_DEPLOYER_PRIVATE_KEY')
accounts.add(private_key)


DEPLOYER=accounts[len(accounts)-1]
OWNER=''
HOLDER=''
TARGET_ACCOUNT=''

def main():
    print('Deployer account= {}'.format(DEPLOYER))

    debtcoin = Debtcoin.deploy(HOLDER, {'from':DEPLOYER}, publish_source=PUBLISH_SOURCES)

    vesting = VestingDebug.deploy(debtcoin, OWNER, TARGET_ACCOUNT, {'from':DEPLOYER}, publish_source=PUBLISH_SOURCES)
