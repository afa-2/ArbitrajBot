import datetime
import json


def _save_networks_to_file(dict_with_networks):
    file_path = 'networks.json'
    with open(file_path, 'w') as f:
        json.dump(dict_with_networks, f)


def _get_networks_from_file():
    file_path = 'networks.json'
    with open(file_path) as f:
        dict_with_networks = json.load(f)
    return dict_with_networks


network_last_update = datetime.datetime.strptime('2023-01-10 18:26:47.204538', '%Y-%m-%d %H:%M:%S.%f')

data_and_time_in_str = network_last_update.strftime('%Y-%m-%d %H:%M:%S.%f')
dict = {'date': data_and_time_in_str}

_save_networks_to_file(dict)


dict_2 = _get_networks_from_file()


dage = datetime.datetime.strptime(dict_2['date'], '%Y-%m-%d %H:%M:%S.%f')

print(type(dage))