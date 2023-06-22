import datetime
import requests
import time
import hashlib
import hmac
import logging



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










dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_huobi_many_coin(['eth', 'btc'])

print('-----------------------------------')
print(res)