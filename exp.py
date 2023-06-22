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

    dict_with_networks = {}
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
        print(response)
        if len(response['result']['rows']) > 0:  # если в ответе вообще что-нибудь есть
            for chain in response['result']['rows'][0]['chains']:
                dict_with_params = {}
                dict_with_params['fee'] = float(chain['withdrawFee'])
                dict_with_params['withdraw_min'] = float(chain['withdrawMin'])
                dict_with_params['percentage_fee'] = float(chain['withdrawPercentageFee'])

                dict_with_networks[chain['chain'].upper()] = dict_with_params

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_bybit_one_coin"' \
               f' произошла ошибка: {e}, ' \
               f'response: {response}, '
        logging.error(text)
        time.sleep(30)

    return dict_with_networks

dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_bybit_one_coin(dict_with_keys, 'ETH')

print(res)