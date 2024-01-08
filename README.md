# Debtcoin contracts

## Setup

We use [Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html) framework for testing and development.
```shell
pip install eth-brownie
brownie pm install OpenZeppelin/openzeppelin-contracts@4.8.3
npm -g i ganache-cli
```

## Testing

All tests can be launched using the command
```shell
brownie test
```

## Deploy

Setup environment variables:
```shell
export DEBTCOIN_DEPLOYER_PRIVATE_KEY=<deployer_account_private_key>
```
Set correct HOLDER_ACCOUNT in [deploy.py](scripts/deploy.py)
```shell
brownie run scripts/deploy.py --network=mainnet
```

## Workflow

1. Deploy
1. holder calls ```debtcoin.approve(vesting, max_amount)```
1. holder calls ```vesting.lock(targetAccount, amount, timeDurationSeconds)```
1. targetAccount waits timeDurationSeconds
1. targetAccount calls ```vesting.claim()```
