"""
Это набор функций, которые получают список сетей для перевода монет с биржи на биржу.
Функции, которые получают список сетей с разных бирж, возвращают список словарей, где каждый словарь, это сеть, где:
chain - название сети
fee - комиссия за перевод
deposit_min - минимальная сумма для пополнения
withdraw_min - минимальная сумма для вывода
withdrawPercentageFee - комиссия за вывод в процентах
"""

import datetime
import requests
import time
import hashlib
import hmac
import uuid
import configparser


def _get_networks_from_bybit_one_coin(dict_with_keys:dict, coin:str) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении одной монеты

    :param dict_with_keys: словарь с ключами для доступа к API биржи
    :param coin: монета, для которой нужно получить список сетей
    :return: возвращается словарь, где каждый словарь, это сеть. Более подробное описание словаря в самом верху файла.

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
    """
    api_key = dict_with_keys['bybit']['api_key']
    secret_key = dict_with_keys['bybit']['secret_key']
    coin = coin.upper()

    httpClient = requests.Session()
    recv_window = str(5000)
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
        dict_with_params['fee'] = chain['withdrawFee']
        dict_with_params['deposit_min'] = chain['depositMin']
        dict_with_params['withdraw_min'] = chain['withdrawMin']
        dict_with_params['withdraw_fee'] = chain['withdrawPercentageFee']

        dict_with_networks[chain['chain']] = dict_with_params

    return dict_with_networks


def _get_networks_from_bybit_many_coin(dict_with_keys:dict, coins:list) -> dict:
    """
    Функция получает список сетей для перевода монет с биржи и на биржу Bybit в отношении всех переданных монет
    Возвращает словарь типа:
    {'bybit': {'ETH': {'fee': '0.0035', 'deposit_min': '0', 'withdraw_min': '0.0035', 'withdraw_fee': '0'}, 'ARBI': {'fee': '0.0003', 'deposit_min': '0', 'withdraw_min': '0.0003', 'withdraw_fee': '0'}}},
    """
    dict_with_networks = {}
    for coin in coins:
        dict_with_networks[coin] = _get_networks_from_bybit_one_coin(dict_with_keys, coin)

    #dict_with_networks = {'bybit': dict_with_networks}
    return dict_with_networks


def get_networks_for_transfer_coins(dict_with_keys:dict, coins:list) -> dict:
    """
    Получить сети для перевода монет
    :param dict_with_keys:  словарь с ключами для доступа к биржам по API
    :param coins: список монет
    :return: словарь с биржами и сетями для перевода монет
    """
    dict_with_networks = {}

    # получаем сети с биржи Bybit
    dict_with_networks['bybit'] = _get_networks_from_bybit_many_coin(dict_with_keys, coins)

    # добавляем последнее время обновления
    now = datetime.datetime.now()
    dict_with_networks['last_update'] = now
    return dict_with_networks


dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'}}
coins = ['eth', 'btc']


result = get_networks_for_transfer_coins(dict_with_keys, ['eth', 'btc'])
print(result)