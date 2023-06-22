import datetime
import requests
import time
import hashlib
import hmac
import logging


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









dict_with_keys = {'bybit': {'api_key': 'V1IkiWjudAPBY7xsdc', 'secret_key': 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'},
                  'mexc': {'api_key': 'mx0vglCjkyejHhko29', 'secret_key': '0a4699a4461a4b358b50c509e1c1f8e8'},
                  'gate': {'api_key': '90323691e2d247ab1f7bccbf187e6567', 'secret_key': 'a4b8540fc1d95822f79dcf362103e0e253805dd693befb8c0193dddd65384fad'}}


res = _get_networks_from_bitget_many_coin()

print('-----------------------------------')
print(res)