"""
Это набор функций, которые получают список сетей для перевода монет с биржи на биржу.
Функции, которые получают список сетей с разных бирж, возвращают список словарей, где каждый словарь, это сеть, где:
{'bybit': {'eth': {'ETH': {'fee': '0.0019', 'withdraw_min': '0.0019', 'percentage_fee': '0'}, 'ARBI': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'percentage_fee': '0'}, 'BSC': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'percentage_fee': '0'}, 'ZKSYNC': {'fee': '0.00015', 'deposit_min': '0', 'withdraw_min': '0.00015', 'percentage_fee': '0'}, 'OP': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'percentage_fee': '0'}}}, 'last_update': datetime.datetime(2023, 5, 26, 18, 28, 31, 5173)}
chain - название сети
fee - комиссия за перевод
withdraw_min - минимальная сумма для вывода
percentage_fee - комиссия за вывод в процентах
"""

import datetime
import requests
import time
import hashlib
import hmac
import uuid
import configparser


# Биржа Bybit ---------------------------------------------------------------------------------------------------------
def _get_networks_from_bybit_one_coin(dict_with_keys:dict, coin:str) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении одной монеты

    :param dict_with_keys: словарь с ключами для доступа к API биржи
    :param coin: монета, для которой нужно получить список сетей

    При запросе по API с биржи мы получаем словарь, где:
    - "chainType": указывает на тип блокчейна, который используется для транзакций с этой криптовалютой. В данном случае это Ethereum с использованием стандарта ERC20.
    - "confirmation": указывает на количество подтверждений транзакции, необходимых для ее завершения. В данном случае это 64 подтверждения.
    - "withdrawFee": указывает на комиссию, которую пользователь должен заплатить при выводе этой криптовалюты с биржи. В данном случае это 0,0035 ETH.
    - "depositMin": указывает на минимальную сумму, которую пользователь должен внести на биржу для пополнения своего счета. В данном случае это 0 ETH, то есть пользователь может внести любую сумму.
    - "withdrawMin": указывает на минимальную сумму, которую пользователь может вывести с биржи. В данном случае это 0,0035 ETH.
    - "chain": указывает на название блокчейна, который используется для этой криптовалюты. В данном случае это Ethereum (ETH).
    - "chainDeposit": указывает на номер блокчейна, который используется для пополнения счета на бирже. В данном случае это 1, что соответствует Ethereum.
    - "chainWithdraw": указывает на номер блокчейна, который используется для вывода этой криптовалюты с биржи. В данном случае это также 1, что соответствует Ethereum.
    - "minAccuracy": указывает на минимальную точность дробной части при работе с этой криптовалютой. В данном случае это 8 знаков после запятой.
    - "withdrawPercentageFee": указывает на процент комиссии, который биржа берет с пользователей при выводе этой криптовалюты. В данном случае это 0, то есть биржа не бет комиссию за вывод.

    Функция возвращает словарь типа:
    {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
    'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}}
    """
    api_key = dict_with_keys['bybit']['api_key']
    secret_key = dict_with_keys['bybit']['secret_key']
    coin = coin.upper()

    httpClient = requests.Session()
    recv_window = str(50000)
    url = "https://api.bybit.com"

    def HTTP_Request(endPoint, method, payload, Info):
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        if (method == "POST"):
            response = httpClient.request(method, url + endPoint, headers=headers, data=payload)
        else:
            response = httpClient.request(method, url + endPoint + "?" + payload, headers=headers)
        return response.json()

    def genSignature(payload):
        param_str = str(time_stamp) + api_key + recv_window + payload
        hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    dict_with_networks = {}

    endpoint = "/v5/asset/coin/query-info"
    method = "GET"
    params = f"coin={coin}"
    result = HTTP_Request(endpoint, method, params, "List")

    for chain in result['result']['rows'][0]['chains']:
        dict_with_params = {}
        dict_with_params['fee'] = float(chain['withdrawFee'])
        dict_with_params['withdraw_min'] = float(chain['withdrawMin'])
        dict_with_params['percentage_fee'] = float(chain['withdrawPercentageFee'])

        dict_with_networks[chain['chain'].upper()] = dict_with_params

    return dict_with_networks


def _get_networks_from_bybit_many_coin(dict_with_keys:dict, coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении всех переданных монет
    Возвращает словарь типа:
    {'ETH': {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            'BSC': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}},
     'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}}}

    """
    dict_with_networks = {}
    for coin in coins:
        dict_with_networks[coin.upper()] = _get_networks_from_bybit_one_coin(dict_with_keys, coin)

    return dict_with_networks


# Биржа Mexc ---------------------------------------------------------------------------------------------------------
def _get_networks_from_mexc_many_coin(dict_with_keys: dict) -> dict:
    """
    Функция получает список всех сетей для перевода всех монет c биржи mexc
    :param dict_with_keys: словарь с ключами для доступа к API биржи

    При запросе по API с биржи мы получаем словарь, где:
    Примерный словарь: 'coin': 'ETH', 'name': 'ETH', 'networkList': [{'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 64, 'name': 'Ethereum', 'network': 'ERC20', 'withdrawEnable': True, 'withdrawFee': '0.001500000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '6000.000000000000000000', 'withdrawMin': '0.004000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None}]
    - 'name': 'ETH' - это название криптовалюты Ethereum.
    - 'networkList': - список сетей, в которых можно переводить монету.
    - 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.' - это описание, которое говорит о том, что на данный момент невозможно пополнить кошелек криптовалюты Ethereum из-за технических работ.
    - 'depositEnable': True - это параметр, который указывает, разрешено ли пополнение кошелька криптовалюты.
    - 'minConfirm': 64 - это минимальное количество подтверждений, которые должны быть получены для транзакции с криптовалютой Ethereum.
    - 'name': 'Ethereum' - это название сети Ethereum.
    - 'network': 'ERC20' - это протокол, используемый для транзакций с криптовалютой.
    - 'withdrawEnable': True - это параметр, который указывает, разрешено ли выводить криптовалюту Ethereum.
    - 'withdrawFee': '0.001500000000000000' - это комиссия, которую необходимо заплатить при выводе криптовалюты.
    - 'withdrawIntegerMultiple': None - это параметр, который указывает, должна ли криптовалюта Ethereum выводиться в целых числах или нет.
    - 'withdrawMax': '6000.000000000000000000' - это максимальное количество криптовалюты, которое можно вывести за один раз.
    - 'withdrawMin': '0.004000000000000000' - это минимальное количество криптовалюты Ethereum, которое можно вывести за один раз.
    - 'sameAddress': False - это параметр, который указывает, можно ли использовать один и тот же адрес для пополнения и вывода криптовалюты Ethereum.
    - 'contract': '' - это адрес контракта, который используется для транзакций с криптовалютой Ethereum.
    - 'withdrawTips': None - это подсказка, которая может помочь пользователям при выводе криптовалюты.
    - 'depositTips': None - это подсказка, которая может помочь пользователям при пополнении кошелька криптовалюты Ethereum.

    Возвращает словарь типа
    {'ETH': {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            'BSC': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}},
     'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}}}
    """
    api_key = dict_with_keys['mexc']['api_key']
    secret_key = dict_with_keys['mexc']['secret_key']

    payload = {
        'timestamp': str(int(time.time() * 10 ** 3))
    }

    # create signature
    query_string = '&'.join([f"{k}={v}" for k, v in payload.items()])
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    # add signature to payload
    payload['signature'] = signature

    # send request
    url = 'https://api.mexc.com/api/v3/capital/config/getall'
    headers = {'X-MEXC-APIKEY': api_key}
    response = requests.get(url, headers=headers, params=payload)
    response = response.json()

    dict_wint_coins_and_networks = {}
    for row_with_coin_and_list_networks in response:
        coin = row_with_coin_and_list_networks['coin'].upper()
        dict_wint_coins_and_networks[coin] = {}

        for row_network in row_with_coin_and_list_networks['networkList']:
            network = row_network['network'].upper()
            fee = float(row_network['withdrawFee'])
            withdraw_min = float(row_network['withdrawMin'])
            percentage_fee = 0
            dict_wint_coins_and_networks[coin][network] = {'fee': fee, 'withdraw_min': withdraw_min,
                                                           'percentage_fee': percentage_fee}

    return dict_wint_coins_and_networks


# Биржа Kucoin ---------------------------------------------------------------------------------------------------------
def _get_networks_from_kucoin_one_coin(coin: str) -> dict:
    """
    Функция получает сети для одной монеты с биржи Kucoin
    :param coin: название монеты

    При запросе с биржи Kucoin по указанному api получаем словаряь типа:
    {'code': '200000', 'data':
    {'currency': 'ETH', 'name': 'ETH', 'fullName': 'Ethereum', 'precision': 8, 'confirms': None, 'contractAddress': None, 'isMarginEnabled': True, 'isDebitEnabled': True,
    'chains': [
    {'chainName': 'OPTIMISM', 'chain': 'optimism', 'withdrawalMinSize': '0.01', 'withdrawalMinFee': '0.001', 'isWithdrawEnabled': False, 'isDepositEnabled': False, 'confirms': 100, 'contractAddress': ''},
    {'chainName': 'ERC20', 'chain': 'eth', 'withdrawalMinSize': '0.01', 'withdrawalMinFee': '0.005', 'isWithdrawEnabled': True, 'isDepositEnabled': True, 'confirms': 64, 'contractAddress': ''}
    ]}}
    Где:
    chains - список сетей
    chainName - название сети
    chain - название сети
    withdrawalMinSize - минимальная сумма вывода
    withdrawalMinFee - минимальная комиссия вывода
    isWithdrawEnabled - возможность вывода
    isDepositEnabled - возможность депозита
    confirms - количество подтверждений
    contractAddress - адрес контракта

    Возвращает словарь с сетями вида:
    {
    'OPTIMISM': {'fee': '0.0035', 'deposit_min': '0', 'withdraw_min': '0.0035', 'percentage_fee': '0'},
    'ERC20': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'percentage_fee': '0'}
    }
    """
    dict_for_return = {}  # словарь для возврата

    coin = coin.upper()
    url = f'https://api.kucoin.com/api/v2/currencies/{coin}'
    res = requests.get(url).json()
    chains = res['data']['chains']

    for chain in chains:
        fee = float(chain['withdrawalMinFee'])
        withdraw_min = float(chain['withdrawalMinSize'])
        percentage_fee = 0
        dict_for_return[chain['chainName']] = {'fee': fee,
                                               'withdraw_min': withdraw_min,
                                               'percentage_fee': percentage_fee}

    return dict_for_return


def _get_networks_from_kucoin_many_coin(coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Kukoin в отношении всех переданных монет
    Возвращает словарь типа
    {'ETH': {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            'BSC': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}},
     'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}}}
    """

    dict_with_networks = {}
    for coin in coins:
        dict_with_networks[coin.upper()] = _get_networks_from_kucoin_one_coin(coin)

    return dict_with_networks


# Биржа Huobi ---------------------------------------------------------------------------------------------------------
def _get_networks_from_huobi_one_coin(coin: str) -> dict:
    """
    Функция получает сети для одной монеты с биржи Kucoin
    :param coin: название монеты

    {'code': 200, 'data': [{'currency': 'eth', 'assetType': 1,
    'chains': [{'chain': 'arbieth', 'displayName': 'ARBIETH', 'fullName': 'Arbitrum One', 'isDynamic': True, 'numOfConfirmations': 64, 'numOfFastConfirmations': 32, 'depositStatus': 'allowed', 'minDepositAmt': '0.005', 'withdrawStatus': 'prohibited', 'minWithdrawAmt': '0.005', 'withdrawPrecision': 8, 'maxWithdrawAmt': '80.000000000000000000', 'withdrawQuotaPerDay': '80.000000000000000000', 'withdrawQuotaPerYear': None, 'withdrawQuotaTotal': None, 'withdrawFeeType': 'fixed', 'transactFeeWithdraw': '0.00102', 'addrWithTag': False, 'addrDepositTag': False},
               {'chain': 'btt2eth', 'displayName': 'BTT', 'fullName': '', 'baseChain': 'BTT', 'baseChainProtocol': 'BTTRC20', 'isDynamic': False, 'numOfConfirmations': 64, 'numOfFastConfirmations': 32, 'depositStatus': 'allowed', 'minDepositAmt': '0.0003', 'withdrawStatus': 'allowed', 'minWithdrawAmt': '0.0003', 'withdrawPrecision': 8, 'maxWithdrawAmt': '590.000000000000000000', 'withdrawQuotaPerDay': '590.000000000000000000', 'withdrawQuotaPerYear': None, 'withdrawQuotaTotal': None, 'withdrawFeeType': 'fixed', 'transactFeeWithdraw': '0.000036', 'addrWithTag': False, 'addrDepositTag': False}]}
    Где:
    chains - список сетей
    chain - название сети
    displayName - название сети
    minWithdrawAmt - минимальная сумма вывода
    transactFeeWithdraw - минимальная комиссия вывода
    withdrawStatus - возможность вывода
    depositStatus - возможность депозита
    numOfConfirmations - количество подтверждений

    Возвращает словарь с сетями вида:
    {
    'OPTIMISM': {'fee': '0.0035', 'deposit_min': '0', 'withdraw_min': '0.0035', 'percentage_fee': '0'},
    'ERC20': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'percentage_fee': '0'}
    }
    """
    dict_for_return = {}  # словарь для возврата
    coin = coin.lower()
    url = f'https://api.huobi.pro/v2/reference/currencies?currency={coin}'
    res = requests.get(url).json()
    chains = res['data'][0]['chains']

    for chain in chains:
        fee = float(chain['transactFeeWithdraw'])
        withdraw_min = float(chain['minWithdrawAmt'])
        percentage_fee = 0
        dict_for_return[chain['displayName']] = {'fee': fee,
                                               'withdraw_min': withdraw_min,
                                               'percentage_fee': percentage_fee}
    return dict_for_return


# Биржа bitget --------------------------------------------------------------------------------------------------------
def _get_networks_from_bitget_many_coin():
    """
    Функция получает список всех сетей для перевода всех монет c биржи bitget

    При запросе по API с биржи мы получаем словарь вида:
    {'code': '00000', 'msg': 'success', 'requestTime': 0,
    'data': [{'coinId': '1', 'coinName': 'BTC', 'transfer': 'true',
                'chains': [{'chain': 'BTC', 'needTag': 'false', 'withdrawable': 'true', 'rechargeable': 'true', 'withdrawFee': '0.0005', 'extraWithDrawFee': '0', 'depositConfirm': '1', 'withdrawConfirm': '1', 'minDepositAmount': '0.0001', 'minWithdrawAmount': '0.002', 'browserUrl': 'https://blockchair.com/bitcoin/transaction/'},
                           {'chain': 'BEP20', 'needTag': 'false', 'withdrawable': 'true', 'rechargeable': 'true', 'withdrawFee': '0.0000051', 'extraWithDrawFee': '0', 'depositConfirm': '15', 'withdrawConfirm': '15', 'minDepositAmount': '0.000001', 'minWithdrawAmount': '0.0000078', 'browserUrl': 'https://bscscan.com/tx/'}]},
            {'coinId': '2', 'coinName': 'USDT', 'transfer': 'true',
                'chains': [{'chain': 'OMNI', 'needTag': 'false', 'withdrawable': 'false', 'rechargeable': 'false', 'withdrawFee': '15', 'extraWithDrawFee': '0', 'depositConfirm': '1', 'withdrawConfirm': '1', 'minDepositAmount': '50', 'minWithdrawAmount': '100', 'browserUrl': 'https://www.omniexplorer.info/tx/'}]}]}

    Где:
    - 'coinId': '1' - это id монеты
    - 'coinName': 'BTC' - это название монеты
    - 'transfer': 'true' - это параметр, который указывает, можно ли переводить монету на другой адрес
    - 'chains' - это список сетей, которые можно использовать для перевода монеты
    - 'chain': 'BTC' - это название сети
    - 'needTag': 'false' - это параметр, который указывает, нужен ли тег для перевода монеты
    - 'withdrawable': 'true' - это параметр, который указывает, можно ли переводить монету на другой адрес
    - 'rechargeable': 'true' - это параметр, который указывает, можно ли пополнять монету
    - 'withdrawFee': '0.0005' - это комиссия за перевод монеты
    - 'extraWithDrawFee': '0' - это дополнительная комиссия за перевод монеты
    - 'depositConfirm': '1' - это количество подтверждений для пополнения монеты
    - 'withdrawConfirm': '1' - это количество подтверждений для перевода монеты
    - 'minDepositAmount': '0.0001' - это минимальная сумма для пополнения монеты
    - 'minWithdrawAmount': '0.002' - это минимальная сумма для перевода монеты
    - 'browserUrl': 'https://blockchair.com/bitcoin/transaction/' - это ссылка на браузер, где можно посмотреть транзакцию

    Функция возвращает словарь вида:
    {'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.002, 'percentage_fee': 0.0},
            'BEP20': {'fee': 5.1e-06, 'withdraw_min': 7.8e-06, 'percentage_fee': 0.0}},
    'USDT': {'OMNI': {'fee': 15.0, 'withdraw_min': 100.0, 'percentage_fee': 0.0}}}
    """
    dict_wint_coins_and_networks = {}

    url = f'https://api.bitget.com/api/spot/v1/public/currencies'
    res = requests.get(url).json()

    data = res['data']
    for row_with_coin in data:
        coin = row_with_coin['coinName'].upper()
        dict_wint_coins_and_networks[coin] = {}

        for row_network in row_with_coin['chains']:
            network = row_network['chain'].upper()
            fee = float(row_network['withdrawFee'])
            withdraw_min = float(row_network['minWithdrawAmount'])
            percentage_fee = 0
            dict_wint_coins_and_networks[coin][network] = {'fee': fee, 'withdraw_min': withdraw_min,
                                                           'percentage_fee': percentage_fee}

    return dict_wint_coins_and_networks


def _get_networks_from_huobi_many_coin(coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Huobi в отношении всех переданных монет
    Возвращает словарь типа
    {'ETH': {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            'BSC': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}},
     'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}}}
    """

    dict_with_networks = {}
    for coin in coins:
        dict_with_networks[coin.upper()] = _get_networks_from_huobi_one_coin(coin)

    return dict_with_networks


# Общая функция, которая получает сети со всех бирж -------------------------------------------------------------------
def get_networks_for_transfer_coins(dict_with_keys:dict, coins:list) -> dict:
    """
    Получить сети для перевода монет
    :param dict_with_keys:  словарь с ключами для доступа к биржам по API
    :param coins: список монет
    :return: словарь с биржами и сетями для перевода монет
    """

    dict_with_networks = {}

    # добавляем последнее время обновления
    now = datetime.datetime.now()
    dict_with_networks['last_update'] = now

    # получаем сети с биржи Bybit
    dict_with_networks['bybit'] = _get_networks_from_bybit_many_coin(dict_with_keys, coins)

    # получаем сети с биржи mexc
    dict_with_networks['mexc'] = _get_networks_from_mexc_many_coin(dict_with_keys)

    # получаем сети с биржи Kucoin
    dict_with_networks['kucoin'] = _get_networks_from_kucoin_many_coin(coins)

    # получаем сети с биржи Huobi
    dict_with_networks['huobi'] = _get_networks_from_huobi_many_coin(coins)

    # получаем сети с биржи Bitget
    dict_with_networks['bitget'] = _get_networks_from_bitget_many_coin()

    return dict_with_networks


dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'}}
coins = ['eth', 'btc']




result = _get_networks_from_huobi_many_coin(['eth', 'btc'])
result = get_networks_for_transfer_coins(dict_with_keys, coins)

for i in result:
    print(i, result[i])