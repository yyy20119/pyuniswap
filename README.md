# Pyuniswap


[![License](http://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/yyy20119/pyuniswap/main/LICENSE)

An open source python wrapper for [Uniswap V2](https://uniswap.exchange/).

Provide a very simple way to trade in Uniswap with python.

## Installation
You may manually install the project or use pip:

```python
pip install pyuniswap

# or

pip install git+git://github.com/yyy20119/pyuniswap.git
```

## Quick Start
```python
from pyuniswap import pyuniswap

#target token address
prq_address = '0x362bc847a3a9637d3af6624eec853618a43ed7d2'

#your provider here
my_provider = 'https://mainnet.infura.io/v3/'

#Token object(every token is a object in pyuniswap)
prq = Token(prq_address, my_provider)

#connect your wallet
prq.connect_wallet('waller_address', 'private_key')

#check whether connected
prq.is_connected()

#token balance(the amount of token in your wallet)
balance=prq.balance()

#price of your token(default the amount of eth if swapping)
prq.price(balance)

#amount of the token(prq) received by swapping 1eth
prq.received_amount_by_swap(int(1e18)))

#swap 1eth to the token(prq)
prq.buy(int(1e18), slippage=0.05)
```

## Github

More details:https://github.com/yyy20119/pyuniswap

**Pull requests are welcome!**



