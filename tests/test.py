from pyuniswap import pyuniswap
prq_address = '0x362bc847a3a9637d3af6624eec853618a43ed7d2'
my_provider = 'https://mainnet.infura.io/v3/'
prq = pyuniswap.Token(prq_address, my_provider)
prq.connect_wallet('0x54e194f0CCEA977D81C0681e8292891c8B8807Bb', '')
print(prq.is_connected())
balance = prq.balance()
print(balance)
print(prq.price(balance))