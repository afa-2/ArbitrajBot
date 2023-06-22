import json


def _get_networks_from_file():
    file_path = 'networks.json'
    with open(file_path) as f:
        dict_with_networks = json.load(f)
    return dict_with_networks


dict_with_networks = _get_networks_from_file()

exchanges = ['bybit', 'mexc', 'kucoin', 'huobi', 'gate', 'bitget']

exchange = 'bitget'

dict_with_networks = dict_with_networks[exchange]

list_with_networks = []
for coin in dict_with_networks:
    all_with_networks_for_this_coin = dict_with_networks[coin]
    for row_networks in all_with_networks_for_this_coin:
        for networks_name in row_networks['network_names']:
            if networks_name not in list_with_networks:
                list_with_networks.append(networks_name)

for i in list_with_networks:
    print(i)
