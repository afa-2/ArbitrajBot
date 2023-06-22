import datetime
import requests
import time
import hashlib
import hmac
import logging



def _get_networks_from_bybit_one_coin(dict_with_keys:dict, coin:str) -> dict:
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
    [{'network_names': ['ERC20', 'ETH'], 'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
    {'network_names': ['ARBITRUM ONE', 'ARBI'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
    {'network_names': ['BSC (BEP20)', 'BSC'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
    {'network_names': ['ZKSYNC LITE', 'ZKSYNC'], 'fee': 0.00015, 'withdraw_min': 0.00015, 'percentage_fee': 0.0},
    {'network_names': ['OPTIMISM', 'OP'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}]
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
                dict_with_params['network_names'] = [str(chain['chainType']).upper(), str(chain['chain']).upper()]
                dict_with_params['fee'] = float(chain['withdrawFee'])
                dict_with_params['withdraw_min'] = float(chain['withdrawMin'])
                dict_with_params['percentage_fee'] = float(chain['withdrawPercentageFee'])

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
    {'ETH': [{'network_names': ['ERC20', 'ETH'], 'fee': 0.0019, 'withdraw_min': 0.0019, 'percentage_fee': 0.0},
            {'network_names': ['ARBITRUM ONE', 'ARBI'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            {'network_names': ['BSC (BEP20)', 'BSC'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0},
            {'network_names': ['ZKSYNC LITE', 'ZKSYNC'], 'fee': 0.00015, 'withdraw_min': 0.00015, 'percentage_fee': 0.0},
            {'network_names': ['OPTIMISM', 'OP'], 'fee': 0.0003, 'withdraw_min': 0.0003, 'percentage_fee': 0.0}],
    'BTC': [{'network_names': ['BTC', 'BTC'], 'fee': 0.0005, 'withdraw_min': 0.0005, 'percentage_fee': 0.0}]}
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


















dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_bybit_many_coin(dict_with_keys, ['eth', 'btc'])

print('-----------------------------------')
print(res)