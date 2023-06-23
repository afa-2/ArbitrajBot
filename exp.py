import json

def _get_networks_from_file():
    file_path = 'networks.json'
    with open(file_path) as f:
        dict_with_networks = json.load(f)
    return dict_with_networks

dict = _get_networks_from_file()

print(dict['huobi'])