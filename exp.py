import datetime
import requests
import time
import hashlib
import hmac
import logging


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
    {'BTC': [{'network_names': ['BTC'], 'fee': 0.001, 'withdraw_min': 0.011},
            {'network_names': ['BSC'], 'fee': 0.00014, 'withdraw_min': 0.011},
            {'network_names': ['HT'], 'fee': 1.7e-05, 'withdraw_min': 0.011}],
    'ETH': [{'network_names': ['ETH'], 'fee': 0.0018, 'withdraw_min': 0.0118},
            {'network_names': ['ARBNOVA'], 'fee': 0.002, 'withdraw_min': 0.0118},
            {'network_names': ['ZKSERA'], 'fee': 0.002, 'withdraw_min': 0.0118},
            {'network_names': ['OPETH'], 'fee': 0.002, 'withdraw_min': 0.0118}]}
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
            dict_with_coins_and_networks[coin] = []
            if 'withdraw_fix_on_chains' in row:
                for network in row['withdraw_fix_on_chains']:
                    dict_with_parameters = {}
                    # название сети
                    network_name = str(network).upper()
                    dict_with_parameters['network_names'] = [network_name]
                    # комиссия
                    fee = float(row['withdraw_fix_on_chains'][network])
                    dict_with_parameters['fee'] = fee
                    # минимальная сумма вывода
                    withdraw_min = float(row['withdraw_amount_mini'])
                    dict_with_parameters['withdraw_min'] = withdraw_min

                    dict_with_coins_and_networks[coin].append(dict_with_parameters)

    except Exception as e:
        text = f'При выполнении функции "_get_networks_from_gate_many_coin" произошла ошибка: {e}' \
               f'response: {response}'
        logging.error(text)

    return dict_with_coins_and_networks









dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_gate_many_coin(dict_with_keys)

print('-----------------------------------')
print(res)