import datetime
import requests
import time
import hashlib
import hmac
import logging


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
                dict_with_network_params['network_names'] = [str(chain['chainName']).upper(), str(chain['chain']).upper()]
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














dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_kucoin_many_coin(['eth', 'btc'])

print('-----------------------------------')
print(res)