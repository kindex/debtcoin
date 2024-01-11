import os

PUBLISH_SOURCES=True

private_key=os.getenv('DEBTCOIN_DEPLOYER_PRIVATE_KEY')
accounts.add(private_key)

HOLDER=''
TARGET_ACCOUNT=''
OWNER=''

def main():
    print('Deployer account= {}'.format(accounts[0]))

    debtcoin = Debtcoin.deploy(HOLDER_ACCOUNT, {'from':accounts[0]}, publish_source=PUBLISH_SOURCES)

    vesting = Vesting.deploy(debtcoin, {'from':accounts[0]}, publish_source=PUBLISH_SOURCES)
