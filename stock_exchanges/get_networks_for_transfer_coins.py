import datetime
import requests
import time
import hashlib
import hmac
import logging


# Биржа Bybit ---------------------------------------------------------------------------------------------------------
def _get_networks_from_bybit_one_coin(dict_with_keys:dict, coin:str) -> list:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении одной монеты

    :param dict_with_keys: словарь с ключами для доступа к API биржи
    :param coin: монета, для которой нужно получить список сетей

    При запросе по API с биржи мы получаем словарь:
     'retCode': 0, 'retMsg': '', 'result': {'rows': [
     {'name': 'ETH', 'coin': 'ETH', 'remainAmount': '10000', 'chains': [
       {'chainType': 'ERC20', 'confirmation': '6', 'withdrawFee': '0.0019', 'depositMin': '0', 'withdrawMin': '0.0019', 'chain': 'ETH', 'chainDeposit': '1', 'chainWithdraw': '1', 'minAccuracy': '8', 'withdrawPercentageFee': '0'},
       {'chainType': 'Arbitrum One', 'confirmation': '12', 'withdrawFee': '0.0003', 'depositMin': '0', 'withdrawMin': '0.0003', 'chain': 'ARBI', 'chainDeposit': '1', 'chainWithdraw': '1', 'minAccuracy': '8', 'withdrawPercentageFee': '0'},
       {'chainType': 'BSC (BEP20)', 'confirmation': '15', 'withdrawFee': '0.0003', 'depositMin': '0', 'withdrawMin': '0.0003', 'chain': 'BSC', 'chainDeposit': '1', 'chainWithdraw': '1', 'minAccuracy': '8', 'withdrawPercentageFee': '0'}}

     где:
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

    Функция возвращает список сетей типа:
    [{'network_names': ['ERC20', 'ETH'], 'fee': 0.0019, 'withdraw_min': 0.0019},
    {'network_names': ['ARBITRUM ONE', 'ARBI'], 'fee': 0.0003, 'withdraw_min': 0.0003},
    {'network_names': ['BSC (BEP20)', 'BSC'], 'fee': 0.0003, 'withdraw_min': 0.0003},
    {'network_names': ['ZKSYNC LITE', 'ZKSYNC'], 'fee': 0.00015, 'withdraw_min': 0.00015},
    {'network_names': ['OPTIMISM', 'OP'], 'fee': 0.0003, 'withdraw_min': 0.0003}]
    """

    def _genSignature(payload, api_key, recv_window, secret_key):
        param_str = str(time_stamp) + api_key + recv_window + payload
        hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    def _HTTP_Request(endPoint, method, payload, url, api_key, secret_key, recv_window):
        httpClient = requests.Session()
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = _genSignature(payload, api_key, recv_window, secret_key)
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

    list_with_networks = []
    response = ''

    try:
        url = "https://api.bybit.com"
        api_key = dict_with_keys['bybit']['api_key']
        secret_key = dict_with_keys['bybit']['secret_key']
        coin = coin.upper()

        recv_window = str(50000)

        endpoint = "/v5/asset/coin/query-info"
        method = "GET"
        params = f"coin={coin}"
        response = _HTTP_Request(endpoint, method, params, url, api_key, secret_key, recv_window)

        if len(response['result']['rows']) > 0:  # если в ответе вообще что-нибудь есть
            for chain in response['result']['rows'][0]['chains']:
                dict_with_params = {}

                dict_with_params['network_names'] = []
                network_names = [chain['chainType'], chain['chain']]
                for network_name in network_names:
                    network_name = str(network_name).upper()
                    if network_name != '' and network_name not in dict_with_params['network_names']:
                        dict_with_params['network_names'].append(network_name)

                dict_with_params['fee'] = float(chain['withdrawFee'])
                dict_with_params['withdraw_min'] = float(chain['withdrawMin'])

                list_with_networks.append(dict_with_params)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_bybit_one_coin"' \
               f' произошла ошибка: {e}, ' \
               f'response: {response}, '
        logging.error(text)
        time.sleep(30)

    return list_with_networks


def _get_networks_from_bybit_many_coin(dict_with_keys:dict, coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении всех переданных монет
    Возвращает словарь типа:
    {'ETH': [{'network_names': ['ERC20', 'ETH'], 'fee': 0.0019, 'withdraw_min': 0.0019},
            {'network_names': ['ARBITRUM ONE', 'ARBI'], 'fee': 0.0003, 'withdraw_min': 0.0003},
            {'network_names': ['BSC (BEP20)', 'BSC'], 'fee': 0.0003, 'withdraw_min': 0.0003},
            {'network_names': ['ZKSYNC LITE', 'ZKSYNC'], 'fee': 0.00015, 'withdraw_min': 0.00015},
            {'network_names': ['OPTIMISM', 'OP'], 'fee': 0.0003, 'withdraw_min': 0.0003}],
    'BTC': [{'network_names': ['BTC', 'BTC'], 'fee': 0.0005, 'withdraw_min': 0.0005}]}
    """
    dict_with_networks = {}

    try:
        for coin in coins:
            dict_with_networks[coin.upper()] = _get_networks_from_bybit_one_coin(dict_with_keys, coin)
            time.sleep(0.5)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_bybit_many_coin" произошла ошибка: {e}'
        logging.error(text)

    return dict_with_networks


# Биржа Mexc ---------------------------------------------------------------------------------------------------------
def _get_networks_from_mexc_many_coin(dict_with_keys: dict) -> dict:
    """
    Функция получает список всех сетей для перевода всех монет c биржи mexc
    :param dict_with_keys: словарь с ключами для доступа к API биржи

    При запросе по API с биржи мы получаем словарь
    {'coin': 'ETH', 'name': 'ETH', 'networkList': [
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 64, 'name': 'Ethereum', 'network': 'ERC20', 'withdrawEnable': True, 'withdrawFee': '0.001500000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '6000.000000000000000000', 'withdrawMin': '0.004000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 100, 'name': 'Ethereum', 'network': 'Arbitrum One', 'withdrawEnable': True, 'withdrawFee': '0.001000000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '1000.000000000000000000', 'withdrawMin': '0.010000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': False, 'minConfirm': 12, 'name': 'Ethereum', 'network': 'BOBA', 'withdrawEnable': False, 'withdrawFee': '0.001000000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '1000.000000000000000000', 'withdrawMin': '0.003000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 12, 'name': 'ETH-BSC', 'network': 'BEP20(BSC)', 'withdrawEnable': True, 'withdrawFee': '0.000500000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '10000.000000000000000000', 'withdrawMin': '0.001000000000000000', 'sameAddress': False, 'contract': '0x2170ed0880ac9a755fd29b2688956bd959f933f8', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 30, 'name': 'ETH', 'network': 'OP', 'withdrawEnable': True, 'withdrawFee': '0.000600000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '1000.000000000000000000', 'withdrawMin': '0.005000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': False, 'minConfirm': 100, 'name': 'ETH', 'network': 'SOL', 'withdrawEnable': False, 'withdrawFee': '0.000100000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '1200.000000000000000000', 'withdrawMin': '0.000200000000000000', 'sameAddress': False, 'contract': '2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk', 'withdrawTips': None, 'depositTips': 'Due to block scanning delay on SOL, deposits may be slightly delayed.'},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': False, 'minConfirm': 2, 'name': 'ETH', 'network': 'STARKNET', 'withdrawEnable': False, 'withdrawFee': '0.001000000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '1000000.000000000000000000', 'withdrawMin': '0.002000000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 12, 'name': 'Ethereum', 'network': 'TRC20', 'withdrawEnable': True, 'withdrawFee': '0.001000000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '10000.000000000000000000', 'withdrawMin': '0.002000000000000000', 'sameAddress': False, 'contract': 'THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF', 'withdrawTips': None, 'depositTips': None},
      {'coin': 'ETH', 'depositDesc': 'Wallet is under maintenance. Deposit has been suspended.', 'depositEnable': True, 'minConfirm': 4, 'name': 'ETH', 'network': 'zkSync Lite(v1)', 'withdrawEnable': True, 'withdrawFee': '0.000300000000000000', 'withdrawIntegerMultiple': None, 'withdrawMax': '200.000000000000000000', 'withdrawMin': '0.000500000000000000', 'sameAddress': False, 'contract': '', 'withdrawTips': 'The token is currently zkSync Lite 1.0, Please confirm before proceeding.', 'depositTips': 'The token is currently zkSync Lite 1.0, Please confirm before proceeding.'}]}

    где:
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

    Возвращает словарь типа:
    {'ETH': [{'network_names': ['ERC20'], 'fee': 0.0015, 'withdraw_min': 0.004},
            {'network_names': ['ARBITRUM ONE'], 'fee': 0.001, 'withdraw_min': 0.01},
            {'network_names': ['BOBA'], 'fee': 0.001, 'withdraw_min': 0.003},
            {'network_names': ['BEP20(BSC)'], 'fee': 0.0005, 'withdraw_min': 0.001},
            {'network_names': ['OP'], 'fee': 0.0006, 'withdraw_min': 0.005},
            {'network_names': ['SOL'], 'fee': 0.0001, 'withdraw_min': 0.0002},
            {'network_names': ['STARKNET'], 'fee': 0.001, 'withdraw_min': 0.002},
            {'network_names': ['TRC20'], 'fee': 0.001, 'withdraw_min': 0.002},
            {'network_names': ['ZKSYNC LITE(V1)'], 'fee': 0.0003, 'withdraw_min': 0.0005}],
    'BTC': [{'network_names': ['BTC'], 'fee': 0.0003, 'withdraw_min': 0.001},
            {'network_names': ['BEP20(BSC)'], 'fee': 1e-05, 'withdraw_min': 0.0001},
            {'network_names': ['TRC20'], 'fee': 0.0001, 'withdraw_min': 0.001}]}
    """
    dict_wint_coins_and_networks = {}
    response = ''

    try:
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

        for row_with_coin_and_list_networks in response:
            coin = row_with_coin_and_list_networks['coin']
            coin = coin.upper()

            dict_wint_coins_and_networks[coin] = []  # список со словарями. Каждый словарь - параметры сети
            for row_network in row_with_coin_and_list_networks['networkList']:
                dict_with_params_network = {}  # словарь с параметрами сети
                # название сети
                network = row_network['network'].upper()
                dict_with_params_network['network_names'] = [network]
                # комиссия
                fee = float(row_network['withdrawFee'])
                dict_with_params_network['fee'] = fee
                # минимальный размер вывода
                withdraw_min = float(row_network['withdrawMin'])
                dict_with_params_network['withdraw_min'] = withdraw_min
                dict_wint_coins_and_networks[coin].append(dict_with_params_network)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_mexc_many_coin" произошла ошибка: {e}, response: {response}'
        logging.error(text)

    return dict_wint_coins_and_networks


# Биржа Kucoin ---------------------------------------------------------------------------------------------------------
def _get_networks_from_kucoin_one_coin(coin: str) -> list:
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

    Возвращает список с сетями вида:
        [{'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.001, 'withdraw_min': 0.01},
        {'network_names': ['ERC20', 'ETH'], 'fee': 0.005, 'withdraw_min': 0.01},
        {'network_names': ['KCC', 'KCC'], 'fee': 0.0002, 'withdraw_min': 0.01},
        {'network_names': ['TRC20', 'TRX'], 'fee': 0.0005, 'withdraw_min': 0.002},
        {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.001, 'withdraw_min': 0.001}]
    """
    list_for_return = []  # словарь для возврата
    response = ''

    try:
        coin = coin.upper()
        url = f'https://api.kucoin.com/api/v2/currencies/{coin}'
        response = requests.get(url).json()

        if response['code'] != '900003':
            chains = response['data']['chains']

            for chain in chains:
                dict_with_network_params = {}
                # названия сети
                dict_with_network_params['network_names'] = []
                network_names = [chain['chainName'], chain['chain']]
                for network_name in network_names:
                    network_name = str(network_name).upper()
                    if network_name != '' and network_name not in dict_with_network_params['network_names']:
                        dict_with_network_params['network_names'].append(network_name)

                # комиссия
                fee = float(chain['withdrawalMinFee'])
                dict_with_network_params['fee'] = fee
                # минимальный вывод
                withdraw_min = float(chain['withdrawalMinSize'])
                dict_with_network_params['withdraw_min'] = withdraw_min
                list_for_return.append(dict_with_network_params)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_kucoin_one_coin" произошла ошибка: {e}, ' \
               f'response: {response}'
        logging.error(text)
        time.sleep(30)

    return list_for_return


def _get_networks_from_kucoin_many_coin(coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Kukoin в отношении всех переданных монет
    Возвращает словарь типа
    {'ETH': [{'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.001, 'withdraw_min': 0.01},
            {'network_names': ['ERC20', 'ETH'], 'fee': 0.005, 'withdraw_min': 0.01},
            {'network_names': ['KCC', 'KCC'], 'fee': 0.0002, 'withdraw_min': 0.01},
            {'network_names': ['TRC20', 'TRX'], 'fee': 0.0005, 'withdraw_min': 0.002},
            {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.001, 'withdraw_min': 0.001}],
    'BTC': [{'network_names': ['BTC', 'BTC'], 'fee': 0.0005, 'withdraw_min': 0.0008},
            {'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.0001, 'withdraw_min': 0.0005},
            {'network_names': ['KCC', 'KCC'], 'fee': 2e-05, 'withdraw_min': 0.0008},
            {'network_names': ['TRC20', 'TRX'], 'fee': 0.0001, 'withdraw_min': 0.0005},
            {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.0001, 'withdraw_min': 0.0005},
            {'network_names': ['BTC-SEGWIT', 'BECH32'], 'fee': 0.0005, 'withdraw_min': 0.0008}]}
    """
    dict_with_networks = {}

    try:
        for coin in coins:
            dict_with_networks[coin.upper()] = _get_networks_from_kucoin_one_coin(coin)
            time.sleep(0)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_kucoin_many_coin" произошла ошибка: {e}'
        logging.error(text)

    return dict_with_networks


# Биржа Huobi ---------------------------------------------------------------------------------------------------------
def _get_networks_from_huobi_one_coin(coin: str) -> list:
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

    Возвращает список с сетями вида:
        [{'network_names': ['ARBIETH', 'ARBITRUM ONE'], 'fee': 0.00102, 'withdraw_min': 0.005},
        {'network_names': ['BTT2ETH', 'BTT'], 'fee': 3.6e-05, 'withdraw_min': 0.0003},
        {'network_names': ['CUBEETH'], 'fee': 9.49e-06, 'withdraw_min': 0.0005},
        {'network_names': ['ETH', 'ETHEREUM'], 'fee': 0.0012, 'withdraw_min': 0.01},
        {'network_names': ['HRC20ETH'], 'fee': 1.299e-05, 'withdraw_min': 0.05},
        {'network_names': ['OPTETH'], 'fee': 0.001, 'withdraw_min': 0.005}]
    """
    list_for_return = []  # список для возврата
    response = ''

    try:
        coin = coin.lower()
        url = f'https://api.huobi.pro/v2/reference/currencies?currency={coin}'
        response = requests.get(url).json()

        if len(response['data']) > 0:
            chains = response['data'][0]['chains']

            for chain in chains:
                dict_with_network_parameters = {}
                # названия сети
                dict_with_network_parameters['network_names'] = []
                network_names = [chain['chain'], chain['displayName'], chain['fullName']]
                for network_name in network_names:
                    network_name = network_name.upper()
                    if network_name != '' and network_name not in dict_with_network_parameters['network_names']:
                        dict_with_network_parameters['network_names'].append(network_name)

                # комиссия
                fee = float(chain['transactFeeWithdraw'])
                dict_with_network_parameters['fee'] = fee
                # размер минимального вывода
                withdraw_min = float(chain['minWithdrawAmt'])
                dict_with_network_parameters['withdraw_min'] = withdraw_min

                list_for_return.append(dict_with_network_parameters)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_huobi_one_coin" произошла ошибка: {e}, response: {response}'
        logging.error(text)
        time.sleep(30)

    return list_for_return


def _get_networks_from_huobi_many_coin(coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Huobi в отношении всех переданных монет
    Возвращает словарь типа
    {'ETH': [{'network_names': ['ARBIETH', 'ARBITRUM ONE'], 'fee': 0.00102, 'withdraw_min': 0.005},
            {'network_names': ['BTT2ETH', 'BTT'], 'fee': 3.6e-05, 'withdraw_min': 0.0003},
            {'network_names': ['CUBEETH'], 'fee': 9.49e-06, 'withdraw_min': 0.0005},
            {'network_names': ['ETH', 'ETHEREUM'], 'fee': 0.0012, 'withdraw_min': 0.01},
            {'network_names': ['HRC20ETH'], 'fee': 1.299e-05, 'withdraw_min': 0.05},
            {'network_names': ['OPTETH'], 'fee': 0.001, 'withdraw_min': 0.005}],
    'BTC': [{'network_names': ['BTC', 'BITCOIN'], 'fee': 0.001, 'withdraw_min': 0.001},
            {'network_names': ['BTT2BTC', 'BTT'], 'fee': 1e-07, 'withdraw_min': 1.7e-05},
            {'network_names': ['HBTC'], 'fee': 0.00018925, 'withdraw_min': 0.001},
            {'network_names': ['HRC20BTC', 'HBTC'], 'fee': 1.11e-06, 'withdraw_min': 0.001},
            {'network_names': ['TRC20BTC', 'TRX'], 'fee': 5e-05, 'withdraw_min': 0.001}]}
    """

    dict_with_networks = {}

    try:
        for coin in coins:
            dict_with_networks[coin.upper()] = _get_networks_from_huobi_one_coin(coin)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_huobi_many_coin" произошла ошибка: {e}'
        logging.error(text)

    return dict_with_networks


# Биржа bitget --------------------------------------------------------------------------------------------------------
def _get_networks_from_bitget_many_coin() -> dict:
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
    {'BTC': [{'network_names': ['BTC'], 'fee': 0.0005, 'withdraw_min': 0.002},
            {'network_names': ['BEP20'], 'fee': 5.1e-06, 'withdraw_min': 7.8e-06}],
    'USDT': [{'network_names': ['OMNI'], 'fee': 15.0, 'withdraw_min': 100.0},
            {'network_names': ['ERC20'], 'fee': 3.0638816, 'withdraw_min': 1.0},
            {'network_names': ['POLYGON'], 'fee': 1.0, 'withdraw_min': 0.34},
            {'network_names': ['C-CHAIN'], 'fee': 1.0, 'withdraw_min': 50.0},
            {'network_names': ['ARBITRUMONE'], 'fee': 0.1, 'withdraw_min': 4.0},
            {'network_names': ['SOL'], 'fee': 1.0, 'withdraw_min': 2.0},
            {'network_names': ['OPTIMISM'], 'fee': 1.0, 'withdraw_min': 10.0},
            {'network_names': ['BEP20'], 'fee': 0.29, 'withdraw_min': 10.0},
            {'network_names': ['HECO'], 'fee': 0.1, 'withdraw_min': 5.0},
            {'network_names': ['TRC20'], 'fee': 1.0, 'withdraw_min': 10.0},
            {'network_names': ['BTTC'], 'fee': 1.0, 'withdraw_min': 1.0}],
    'ETH': [{'network_names': ['ARBITRUMNOVA'], 'fee': 0.1, 'withdraw_min': 10.0},
            {'network_names': ['ARBITRUMONE'], 'fee': 0.0001, 'withdraw_min': 0.0008},
            {'network_names': ['ZKSYNCERA'], 'fee': 0.0003, 'withdraw_min': 0.001},
            {'network_names': ['ETH'], 'fee': 0.00079, 'withdraw_min': 0.0098},
            {'network_names': ['OPTIMISM'], 'fee': 0.00032, 'withdraw_min': 0.001},
            {'network_names': ['BEP20'], 'fee': 8e-05, 'withdraw_min': 0.00011}]}
    """
    dict_with_coins_and_networks = {}
    response = ''

    try:
        url = f'https://api.bitget.com/api/spot/v1/public/currencies'
        response = requests.get(url).json()

        data = response['data']
        for row_with_coin in data:
            coin = row_with_coin['coinName'].upper()
            dict_with_coins_and_networks[coin] = []

            for row_network in row_with_coin['chains']:
                dict_with_network_parameters = {}
                # название сети
                network = str(row_network['chain']).upper()
                dict_with_network_parameters['network_names'] = [network]
                # комиссия
                fee = float(row_network['withdrawFee'])
                dict_with_network_parameters['fee'] = fee
                # минимальный вывод
                withdraw_min = float(row_network['minWithdrawAmount'])
                dict_with_network_parameters['withdraw_min'] = withdraw_min

                dict_with_coins_and_networks[coin].append(dict_with_network_parameters)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_bitget_many_coin" произошла ошибка: {e}, ' \
               f'response: {response}'
        logging.error(text)

    return dict_with_coins_and_networks


# Биржа gate ----------------------------------------------------------------------------------------------------------
def _get_networks_from_gate_many_coin(dict_with_keys: dict) -> dict:
    """
    Функция получает список сетей для множества монет с биржи gate
    :param dict_with_keys:
    :param dict_with_keys: словарь с ключами для доступа к API биржи
    При запросе по API с биржи мы получаем словарь, следующего вида:
    [{'currency': 'GT', 'name': 'GateToken', 'name_cn': '狗头', 'deposit': '0', 'withdraw_percent': '0%',
    'withdraw_fix': '0.025', 'withdraw_day_limit': '500000', 'withdraw_day_limit_remain': '499999',
    'withdraw_amount_mini': '0.125', 'withdraw_eachtime_limit': '499999',
    'withdraw_fix_on_chains': {'ETH': '0.89', 'GTEVM': '0.002'}},
    {'currency': 'CNYX', 'name': 'CNHT', 'name_cn': 'CNHT', 'deposit': '0', 'withdraw_percent': '0%',
    'withdraw_fix': '10', 'withdraw_day_limit': '20000', 'withdraw_day_limit_remain': '19999',
    'withdraw_amount_mini': '10.1', 'withdraw_eachtime_limit': '19999'}]
    Где:
    - 'currency': 'GT' - это название монеты
    - 'name': 'GateToken' - это название монеты
    - 'name_cn': '狗头' - это название монеты на китайском
    - 'deposit': '0' - это параметр, который указывает, можно ли пополнить монету
    - 'withdraw_percent': '0%' - это процент комиссии за вывод монеты
    - 'withdraw_fix': '0.025' - это фиксированная комиссия за вывод монеты
    - 'withdraw_day_limit': '500000' - это максимальное количество монет, которое можно вывести за один день
    - 'withdraw_day_limit_remain': '499999' - это количество монет, которое можно вывести за один день
    - 'withdraw_amount_mini': '0.125' - это минимальное количество монет, которое можно вывести за один раз
    - 'withdraw_eachtime_limit': '499999' - это максимальное количество монет, которое можно вывести за один раз
    - 'withdraw_fix_on_chains': {'ETH': '0.89', 'GTEVM': '0.002'} - это фиксированная комиссия за вывод монеты на сети

    Функция возвращает словарь типа
    {'ETH': {'ETH': {'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            'ARBI': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            'BSC': {'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}},
     'BTC': {'BTC': {'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}}}
    """
    def gen_sign(method, url, query_string=None, payload_string=None):
        key = dict_with_keys['gate']['api_key']       # api_key
        secret = dict_with_keys['gate']['secret_key']    # api_secret

        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

    dict_with_coins_and_networks = {}
    response = ''

    try:
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/wallet/withdraw_status'
        query_param = ''
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)
        response = requests.request('GET', host + prefix + url, headers=headers)
        data = response.json()

        for row in data:
            coin = row['currency'].upper()
            dict_with_coins_and_networks[coin] = {}
            if 'withdraw_fix_on_chains' in row:
                for network in row['withdraw_fix_on_chains']:
                    fee = float(row['withdraw_fix_on_chains'][network])
                    withdraw_min = float(row['withdraw_amount_mini'])
                    percentage_fee = float(row['withdraw_percent'].replace('%', '')) / 100
                    dict_with_coins_and_networks[coin][network.upper()] = {'fee': fee, 'withdraw_min': withdraw_min,
                                                                   'percentage_fee': percentage_fee}

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_gate_many_coin" произошла ошибка: {e}' \
               f'response: {response}'
        logging.error(text)

    return dict_with_coins_and_networks


# Общая функция, которая получает сети со всех бирж -------------------------------------------------------------------
def get_networks_for_transfer_coins(dict_with_keys:dict, coins:list) -> dict:
    """
    Получить сети для перевода монет
    :param dict_with_keys:  словарь с ключами для доступа к биржам по API
    :param coins: список монет

    Принцип работы: опрашиваем все биржи по api и получаем для каждой монеты сети, через которые можно переводить монеты

    Возвращаемый словарь имеет вид:
    {'last_update': datetime.datetime(2023, 6, 21, 16, 8, 47, 390196),
    'bybit': {'BTC':
                 {'BTC': {'fee': 0.0003, 'withdraw_min': 0.001, 'percentage_fee': 0},
                 'BEP20(BSC)': {'fee': 1e-05, 'withdraw_min': 0.0001, 'percentage_fee': 0},
                 'TRC20': {'fee': 0.0001, 'withdraw_min': 0.001, 'percentage_fee': 0}},
             'DOGE': {'DOGE': {'fee': 5.0, 'withdraw_min': 25.0, 'percentage_fee': 0.0}},
             'LTC': {'LTC': {'fee': 0.001, 'withdraw_min': 0.1, 'percentage_fee': 0.0}}},
    'mexc': {'BTC':
             {'BTC': {'fee': 0.0003, 'withdraw_min': 0.001, 'percentage_fee': 0},
             'BEP20(BSC)': {'fee': 1e-05, 'withdraw_min': 0.0001, 'percentage_fee': 0},
             'TRC20': {'fee': 0.0001, 'withdraw_min': 0.001, 'percentage_fee': 0}},
         'DOGE': {'DOGE': {'fee': 5.0, 'withdraw_min': 25.0, 'percentage_fee': 0.0}},
         'LTC': {'LTC': {'fee': 0.001, 'withdraw_min': 0.1, 'percentage_fee': 0.0}}},
    }
    """

    dict_with_networks = {}

    try:
        # добавляем последнее время обновления
        now = datetime.datetime.now()
        dict_with_networks['last_update'] = now

        # получаем сети с биржи Bybit
        logging.info('Получаем сети с Bybit')
        dict_with_networks['bybit'] = _get_networks_from_bybit_many_coin(dict_with_keys, coins)

        # получаем сети с биржи Mexc
        logging.info('Получаем сети с Mexc')
        dict_with_networks['mexc'] = _get_networks_from_mexc_many_coin(dict_with_keys)

        # получаем сети с биржи Kucoin
        logging.info('Получаем сети с Kucoin')
        dict_with_networks['kucoin'] = _get_networks_from_kucoin_many_coin(coins)

        # получаем сети с биржи Huobi
        logging.info('Получаем сети с Huobi')
        dict_with_networks['huobi'] = _get_networks_from_huobi_many_coin(coins)

        # получаем сети с биржи Bitget
        logging.info('Получаем сети с Bitget')
        dict_with_networks['bitget'] = _get_networks_from_bitget_many_coin()

        # получаем сети с биржи Gate
        logging.info('Получаем сети с Gate')
        dict_with_networks['gate'] = _get_networks_from_gate_many_coin(dict_with_keys)

    except Exception as e:
        text = f'При выполнении функции "get_networks_for_transfer_coins" произошла ошибка: {e}'
        logging.error(text)

    return dict_with_networks




# dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
#                   'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
#                   'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}
# #
# coins = ['eth', 'btc']
#
# result = _get_networks_from_bybit_many_coin(dict_with_keys, coins)
# # result = get_networks_for_transfer_coins(dict_with_keys, coins)
# print(result)