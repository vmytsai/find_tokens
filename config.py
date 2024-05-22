### Выбрать evm или stark
what = 'evm' #  evm | stark

### Настройки для EVM
custom_rpc = ""  # RPC сети в которой будет поиск
check_native = True  # True - есть будем проверять нативку, иначе False
nft = False  # True - есть ищем NFT, иначе False
token_for_check = '0x00000'  # Если check_native = False, надо вставить контракт

### Настройки для Starknet
contract_addr = '0x049D36570D4e46f48e99674bd3fcc84644DdD6b96F7C741B1562B82f9e004dC7'  # Контракт токена который ищем, ниже есть несколько вариантов
node_url = 'https://starknet-mainnet.public.blastapi.io'  # RPC. Если будешь часто юзать иди на инфуру и бери себе RPC (infura.io)

### Контракты для старка:
# ETH:  0x049D36570D4e46f48e99674bd3fcc84644DdD6b96F7C741B1562B82f9e004dC7
# USDT: 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8
# USDC: 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8
# STRK: 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
