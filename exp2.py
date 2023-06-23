import requests

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
        print(response)

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


    return list_for_return

res = _get_networks_from_huobi_one_coin('TENET')
print(res)
