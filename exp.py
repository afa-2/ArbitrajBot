networks_on_exchange_1 = [
    {'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.001, 'withdraw_min': 0.01},
    {'network_names': ['ERC20', 'ETH'], 'fee': 0.0040, 'withdraw_min': 0.01},
    {'network_names': ['KCC', 'KCC'], 'fee': 0.0002, 'withdraw_min': 0.01},
    {'network_names': ['TRC20', 'TRX'], 'fee': 0.0005, 'withdraw_min': 0.002},
    {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.001, 'withdraw_min': 0.001}]

networks_on_exchange_2 = [
    {'network_names': ['CVSDVF', 'DSFVDFF'], 'fee': 0.001, 'withdraw_min': 0.01},
    {'network_names': ['ETH'], 'fee': 0.003, 'withdraw_min': 0.01},
    {'network_names': ['FDGFD', 'FHDRDG'], 'fee': 0.0002, 'withdraw_min': 0.01},
    {'network_names': ['DHDF', 'VBFGN', 'KCC'], 'fee': 0.0005, 'withdraw_min': 0.002},
    {'network_names': ['CBFGBFG', 'DFBGFBF'], 'fee': 0.001, 'withdraw_min': 0.001}]


list_networks_matches = []
for network_exchange_1 in networks_on_exchange_1:
    for network_name_from_exchange_1 in network_exchange_1['network_names']:
        for network_exchange_2 in networks_on_exchange_2:
            if network_name_from_exchange_1 in network_exchange_2['network_names']:
                # названия сети с первой биржи
                network_names_from_exchange_1 = network_exchange_1['network_names']
                # названия сети со второй биржи
                network_names_from_exchange_2 = network_exchange_2['network_names']
                # комиссия в сети с первой биржи
                fee_network_from_exchange_1 = float(network_exchange_1['fee'])
                # комиссия в ети во второй бирже
                fee_network_from_exchange_2 = float(network_exchange_2['fee'])
                # выбираем самую большую комиссию
                fee_network = max(fee_network_from_exchange_1, fee_network_from_exchange_2)

                dict_with_parameters = {}  # словарь с параметрами сети
                # заполняем название
                dict_with_parameters['network_names'] = []
                for network_name in network_names_from_exchange_1 + network_names_from_exchange_2:
                    if network_name not in dict_with_parameters['network_names']:
                        dict_with_parameters['network_names'].append(network_name)
                # заполняем комиссию
                dict_with_parameters['fee'] = fee_network

                if dict_with_parameters not in list_networks_matches:
                    list_networks_matches.append(dict_with_parameters)


print(list_networks_matches)