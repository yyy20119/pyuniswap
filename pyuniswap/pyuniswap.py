from web3 import Web3
import os
import json
import time
from functools import wraps


class Token:
    ETH_ADDRESS = Web3.toChecksumAddress('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
    MAX_AMOUNT = int('0x' + 'f' * 64, 16)

    def __init__(self, address, provider=None):
        self.address = Web3.toChecksumAddress(address)
        self.provider = os.environ['PROVIDER'] if not provider else provider
        self.web3 = Web3(Web3.HTTPProvider(self.provider))
        self.wallet_address = None
        self.router = self.web3.eth.contract(
            address=Web3.toChecksumAddress('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'),
            abi=json.load(open(
                os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/abi_files/" + "router.abi"))))
        self.erc20_abi = json.load(
            open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/abi_files/" + "erc20.abi")))
        self.gas_limit = 1500000

    def connect_wallet(self, wallet_address='', private_key=''):
        self.wallet_address = Web3.toChecksumAddress(wallet_address)
        self.private_key = private_key

    def is_connected(self):
        return False if not self.wallet_address else True

    def require_connected(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.is_connected():
                raise RuntimeError('Please connect the wallet first!')
            return func(self, *args, **kwargs)

        return wrapper

    def create_transaction_params(self, value=0, gas_price=None, gas_limit=None):
        if not self.is_connected():
            raise RuntimeError('Please connect the wallet first!')
        if not gas_price:
            gas_price = self.web3.eth.gasPrice
        if not gas_limit:
            gas_limit = self.gas_limit
        return {
            "from": self.wallet_address,
            "value": value,
            'gasPrice': gas_price,
            "gas": gas_limit,
            "nonce": self.web3.eth.getTransactionCount(self.wallet_address)
        }

    def send_transaction(self, func, params):
        tx = func.buildTransaction(params)
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        return self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    @require_connected
    def is_approved(self, token_address=None, amount=MAX_AMOUNT):
        token_address = Web3.toChecksumAddress(token_address) if token_address else self.address
        erc20_contract = self.web3.eth.contract(address=token_address, abi=self.erc20_abi)
        approved_amount = erc20_contract.functions.allowance(self.wallet_address, self.router.address).call()
        return approved_amount >= amount

    @require_connected
    def approve(self, token_address, amount=MAX_AMOUNT, gas_price=None, timeout=900):
        if not gas_price:
            gas_price = self.web3.eth.gasPrice
        token_address = Web3.toChecksumAddress(token_address)
        erc20_contract = self.web3.eth.contract(address=token_address, abi=self.erc20_abi)
        func = erc20_contract.functions.approve(self.router.address, amount)
        params = self.create_transaction_params(gas_price=gas_price)
        tx = self.send_transaction(func, params)
        self.web3.eth.waitForTransactionReceipt(tx, timeout=timeout)

    def price(self, amount=int(1e18), swap_token_address=ETH_ADDRESS):
        swap_token_address = Web3.toChecksumAddress(swap_token_address)
        return self.router.functions.getAmountsOut(amount, [self.address, swap_token_address]).call()[-1]

    def received_amount_by_swap(self, input_token_amount=int(1e18), input_token_address=ETH_ADDRESS):
        input_token_address = Web3.toChecksumAddress(input_token_address)
        return self.router.functions.getAmountsOut(input_token_amount, [input_token_address, self.address]).call()[-1]

    def balance(self, address=None):
        address = self.wallet_address if not address else Web3.toChecksumAddress(address)
        if not address:
            raise RuntimeError('Please provide the wallet address!')
        erc20_contract = self.web3.eth.contract(address=self.address, abi=self.erc20_abi)
        return erc20_contract.functions.balanceOf(self.wallet_address).call()

    @require_connected
    def buy(self, consumed_token_amount, consumed_token_address=ETH_ADDRESS, slippage=0.01, timeout=900, speed=1):
        gas_price = int(self.web3.eth.gasPrice * speed)
        consumed_token_address = Web3.toChecksumAddress(consumed_token_address)
        received_amount = self.received_amount_by_swap(consumed_token_amount, consumed_token_address)
        min_out = int(received_amount * (1 - slippage))
        if consumed_token_address == self.ETH_ADDRESS:
            func = self.router.functions.swapExactETHForTokens(min_out, [consumed_token_address, self.address],
                                                               self.wallet_address, int(time.time() + timeout))
            params = self.create_transaction_params(value=consumed_token_amount, gas_price=gas_price)
        else:
            if not self.is_approved(consumed_token_address, consumed_token_amount):
                self.approve(consumed_token_address, gas_price=gas_price, timeout=timeout)
            func = self.router.functions.swapExactTokensForTokens(consumed_token_amount, min_out,
                                                                  [consumed_token_address, self.address],
                                                                  self.wallet_address, int(time.time() + timeout))
            params = self.create_transaction_params(gas_price=gas_price)
        return self.send_transaction(func, params)

    @require_connected
    def sell(self, amount, received_token_address=ETH_ADDRESS, slippage=0.01, timeout=900, speed=1):
        gas_price = int(self.web3.eth.gasPrice * speed)
        received_token_address = Web3.toChecksumAddress(received_token_address)
        received_amount = self.price(amount, received_token_address)
        min_out = int(received_amount * (1 - slippage))
        if not self.is_approved(self.address, amount):
            self.approve(self.address, gas_price=gas_price, timeout=timeout)
        if received_token_address == self.ETH_ADDRESS:
            func = self.router.functions.swapExactTokensForETH(amount, min_out, [self.address, received_token_address],
                                                               self.wallet_address, int(time.time() + timeout))
        else:
            func = self.router.functions.swapExactTokensForTokens(amount, min_out,
                                                                  [self.address, received_token_address],
                                                                  self.wallet_address, int(time.time() + timeout))
        params = self.create_transaction_params(gas_price=gas_price)
        return self.send_transaction(func, params)
