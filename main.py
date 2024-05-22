import time
import requests
import platform
import asyncio
import ast
import json
import os

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.cairo.felt import decode_shortstring
from web3 import Web3
from web3 import AsyncWeb3

from data.rpc import RPC
from config import *

clear_text = 'cls' if platform.system().lower() == 'windows' else 'clear'

info = {}

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


async def print_data():
    os.system(clear_text)
    print(f'\nNetwork: {info["0"]["network"]}  |  Wallets: {len(wallets)}  |  Token: {info["0"]["token"]}  |  Price: {info["0"]["price"]} $')
    print('┌──────┬────────────────────────────────────────────┬───────┬───────────────┬─────────────┐')
    print('|  ID  |                  Wallet                    | Trans |    Balance    | Balance USD |')
    print('├──────┼────────────────────────────────────────────┼───────┼───────────────┼─────────────┤')
    for n, data in info.items():
        if n == "0": break
        print(f'| {n:^4} | {data["wallet"]:<42} | {data["nonce"]:<5} | {data["balance"]:<13} | {data["bal_usd"]:<11} |')

    print('├──────┴────────────────────────────────────────────┴───────┼───────────────┼─────────────┤')
    print(f'| Total                                                     | {info["0"]["total"]:<13} | {round(info["0"]["total"] * info["0"]["price"], 3):<11} |')
    print('└───────────────────────────────────────────────────────────┴───────────────┴─────────────┘')


async def set_data():
    for num, wallet in enumerate(wallets):
        info[str(num+1)] = {
            "wallet" : wallet,
            "nonce"  : "░░░░░",
            "balance": "░░░░░░░░░░░░░",
            "bal_usd": "░░░░░░░░░░░"
        }
    info["0"] = {
        "network": "░░░░░░░░░",
        "token"  : "░░░░░",
        "price"  : 0,
        "total"  : 0
    }


async def get_chain():
    rpc_list = {}
    for num, item in enumerate(RPC): rpc_list[num+1] = item
    rpc_list[0] = "Custom"
    print(f'Сhoose a network:\n' + '\n'.join([str(i) + ". " + netw for i, netw in rpc_list.items()]))
    rpc_id = int(input('>>> '))
    info["0"]["network"] = rpc_list[rpc_id]
    return RPC[rpc_list[rpc_id]] if rpc_id != 0 else custom_rpc


async def get_price(token):
    try:
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={token}USDT')
        data = response.json()
        price = float(data['price'])
    except KeyError:
        price = 0

    return price


async def wallet_data(i, wallet, web3, contract, decimal):
    try:
        public = Web3.to_checksum_address(wallet)
    except ValueError:
        os.system(clear_text)
        print(
            'The wallet is not valid, you are probably trying to use Starknet wallets. Change the variable in the config or replace the wallets.')
        return

    nonce = await web3.eth.get_transaction_count(public)

    if not check_native:
        balance_wei = await contract.functions.balanceOf(public).call()
        humanReadable = balance_wei / 10 ** decimal if not nft else balance_wei
    else:
        balance = await web3.eth.get_balance(public)
        humanReadable = float(web3.from_wei(balance, "ether"))

    info["0"]["total"] = round(info["0"]["total"] + float(humanReadable), 7)
    info[i]["nonce"] = nonce
    info[i]["balance"] = round(float(humanReadable), 7) if float(humanReadable) < 10 else round(float(humanReadable), 4)
    info[i]["bal_usd"] = round(float(humanReadable * info["0"]["price"]), 3)
    await print_data()


async def evm():
    await set_data()
    rpcs = await get_chain()
    await print_data()
    n = 0
    total = 0
    web3 = None
    symbol = ''
    decimal = 0
    contract = None
    contract_address = None

    if isinstance(rpcs, str):
        if not rpcs:
            print("Custom RPC not found :(")
            return
        web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpcs))

        if not await web3.is_connected():
            print("RPC doesn't work :(")
            return
    else:
        connected = False
        for rpc in rpcs:
            web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
            if await web3.is_connected():
                connected = True
                break
        if not connected:
            print("RPCs doesn't work :(")
            return

    if not check_native:
        contract_address = Web3.to_checksum_address(token_for_check)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        symbol = await contract.functions.symbol().call()
        if not nft:
            decimal = await contract.functions.decimals().call()
    else:
        with open('data/native.json') as file:
            chains = json.load(file)
        try:
            symbol = chains[str(await web3.eth.chain_id)]
        except KeyError:
            pass

    price = await get_price(symbol)
    if symbol in ['USDT', 'USDC', 'DAI']:
        price = 1
    info["0"]["token"] = symbol
    info["0"]["price"] = price

    await asyncio.gather(*[wallet_data(str(i+1), wallet, web3, contract, decimal) for i, wallet in enumerate(wallets)])

    with open('res.txt', 'a') as res:
        res.write('┌──────┬────────────────────────────────────────────┬───────┬────────────────────────────\n')
        res.write(f'|  ID  |                  Wallet                    | Trans |        Balance\n')
        res.write('├──────┼────────────────────────────────────────────┼───────┼────────────────────────────\n')
        for n, data in info.items():
            if n == "0": break
            res.write(
                f'| {n:^4} | {data["wallet"]:<42} | {data["nonce"]:<5} | {str(data["balance"])+" " + info["0"]["token"]:<15} ({data["bal_usd"]} $)\n')

        res.write('├──────┴────────────────────────────────────────────┴───────┼────────────────────────────\n')
        res.write(f'| Total                                                     | {info["0"]["total"]} {info["0"]["token"]} ({round(info["0"]["total"] * info["0"]["price"], 3)} $)\n')
        res.write('└───────────────────────────────────────────────────────────┴────────────────────────────')


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
    if symbol in ['USDT', 'USDC', 'DAI']:
        price = 1
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
    try:
        asyncio.run(evm() if what == 'evm' else stark())
    except KeyboardInterrupt:
        print('Exit pressed Ctrl+C')
    except asyncio.CancelledError:
        print('id, Asyncio | The work has been canceled')
    except Exception as e:
        print(f'Something went wrong :(\n\n{e}\n')
