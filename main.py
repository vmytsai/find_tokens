import time

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.cairo.felt import decode_shortstring
from web3 import Web3
from web3 import AsyncWeb3
from web3.middleware import async_geth_poa_middleware
import requests
from config import *
import asyncio
import ast
import json

with open('res.txt', 'w'):
    pass

with open('data/abi.json') as file:
    abi = json.load(file)

wallets = []
with open('wallets.txt', 'r') as f:
    for row in f:
        wallet = row.strip()
        if wallet:
            wallets.append(wallet)


def get_price(token):
    try:
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={token}USDT')
        data = response.json()
        price = float(data['price'])
    except KeyError:
        price = 0

    return price


async def evm():
    n = 0
    total = 0
    symbol = ''

    if 'zora' in rpc:
        proxies = {'all': f'http://' + proxy, }
        request_kwargs = {"proxies": proxies, "timeout": 120}

        web3 = Web3(Web3.HTTPProvider(rpc, request_kwargs=request_kwargs))
    else:
        web3 = Web3(Web3.HTTPProvider(rpc))

    if not web3.is_connected():
        print("RPC doesn't work :(")
        return

    if not check_native:
        contract_address = Web3.to_checksum_address(token_for_check)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        symbol = contract.functions.symbol().call()
        if not nft:
            decimal = contract.functions.decimals().call()
    else:
        with open('data/native.json') as file:
            chains = json.load(file)
        try:
            symbol = chains[str(web3.eth.chain_id)]
        except KeyError:
            pass

    price = get_price(symbol)
    print(f'\nWallets: {len(wallets)}  |  Token: {symbol}  |  Price: {price} $\n')

    for i in wallets:

        n += 1
        try:
            public = Web3.to_checksum_address(i)
        except ValueError:
            print(
                'The wallet is not valid, you are probably trying to use Starknet wallets. Change the variable in the config or replace the wallets.')
            return

        nonce = web3.eth.get_transaction_count(public)

        if not check_native:
            balance_wei = contract.functions.balanceOf(public).call()
            humanReadable = balance_wei / 10 ** decimal if not nft else balance_wei
        else:
            balance = web3.eth.get_balance(public)
            humanReadable = float(web3.from_wei(balance, "ether"))

        total += float(humanReadable)
        print(
            f'{n:^3} | {public} | Transactions: {nonce:^4} | Balance: {humanReadable:.7f} {symbol} ({float(humanReadable * price):.3f} $)')

        with open('res.txt', 'a') as res:
            res.write(
                f'{n:^4} | {public} | Transactions: {nonce:^4} | Balance: {humanReadable:.7f} {symbol} ({float(humanReadable * price):.3f} $)\n')
        time.sleep(.2)

    print(f'\nTotal balance: {total:.10} ({float(total * price):.3f} $)')


async def stark():
    client = FullNodeClient(node_url=node_url)
    symbol = await client.call_contract(
        call=Call(
            to_addr=contract_addr,
            selector=get_selector_from_name('symbol'),
            calldata=[],
        ),
        block_number='latest',
    )
    symbol = decode_shortstring(symbol[0])
    decimals = await client.call_contract(
        call=Call(
            to_addr=contract_addr,
            selector=get_selector_from_name('decimals'),
            calldata=[],
        ),
        block_number='latest',
    )
    decimals = decimals[0]

    price = get_price(symbol)
    print(f'\nWallets: {len(wallets)}  |  Token: {symbol}  |  Price: {price} $\n')

    n = 0
    total = 0
    for wallet in wallets:
        n += 1
        try:
            nonce = await client.get_contract_nonce(wallet)
        except ClientError:
            print(
                'The wallet is not valid, you are probably trying to use EVM wallets. Change the variable in the config or replace the wallets.')
            return

        balance = await client.call_contract(
            call=Call(
                to_addr=contract_addr,
                selector=get_selector_from_name('balance_of'),
                calldata=[ast.literal_eval(wallet)],
            ),
            block_number='latest',
        )
        total += balance[0] / 10 ** decimals
        print(
            f'{n:^3} | {wallet} | Transactions: {nonce:^4} | Balance: {balance[0] / 10 ** decimals:.7f} {symbol} ({float((balance[0] / 10 ** decimals) * price):.3f} $)')

        with open('res.txt', 'a') as res:
            res.write(
                f'{n:^3} | {wallet} | Transactions: {nonce:^4} | Balance: {balance[0] / 10 ** decimals:.7f} {symbol} ({float((balance[0] / 10 ** decimals) * price):.3f} $)')
        time.sleep(.2)

    print(f'\nTotal balance: {total:.7} ({float(total * price):.3f} $)')


if __name__ == '__main__':
    asyncio.run(evm() if what == 'evm' else stark())
