### Выбрать evm или stark
what = 'stark' #  evm | stark


### Настройки для EVM
rpc = 'https://avalanche-c-chain-rpc.publicnode.com'  # RPC сути в которой будет поиск. Ниже в файле есть варианты, но можно юзать любые (но не все, пробуйте крч)
check_native = True  # True - есть будем проверять нативку, иначе False
nft = False  # True - есть ищем NFT, иначе False
token_for_check = '0x00000'  # Если check_native = False, надо вставить контракт

### Настройки для Starknet
contract_addr = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d'  # Контракт токена который ищем, ниже есть несколько вариантов
node_url = 'https://starknet-mainnet.public.blastapi.io'  # RPC. Если будешь часто юзать иди на инфуру и бери себе RPC (infura.io)


### Трошки RPC для evm (юзать можно почти все сети):
# Ethereum - https://ethereum-rpc.publicnode.com
# Optimism - https://optimism-rpc.publicnode.com
# Arbitrum - https://arbitrum-one-rpc.publicnode.com
# zkSync   - https://mainnet.era.zksync.io
# Linea    - https://linea.decubate.com
# Base     - https://base-rpc.publicnode.com
# BSC      - https://bsc-rpc.publicnode.com
# Avalance - https://avalanche-c-chain-rpc.publicnode.com
# Polygon  - https://polygon-bor-rpc.publicnode.com


### Контракты для старка:
# ETH:  0x049D36570D4e46f48e99674bd3fcc84644DdD6b96F7C741B1562B82f9e004dC7
# USDT: 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8
# USDC: 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8
# STRK: 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
