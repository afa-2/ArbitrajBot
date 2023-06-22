import datetime
import requests
import time
import hashlib
import hmac
import logging


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

















dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_mexc_many_coin(dict_with_keys)

print('-----------------------------------')
print(res)