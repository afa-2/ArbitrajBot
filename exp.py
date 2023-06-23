
def _add_additional_network_names_to_the_list_of_names(dict_with_network: dict, list_matching_networks: list) -> dict:
    """
    Функция получает:
    Словарь с параметрами сети: {'network_names': ['ETH', 'ETH2'], 'fee': 0.001, 'withdraw_min': 0.01}
    Список совпадений названий: пример: [['BEP20(BSC)', 'BSC'], ['ERC20', 'ETH']]

    Функция берет каждое название из параметра сети и ищет совпадения в списке совпадающих назнваний. Если нашла, то все
    совпадающие названия переносятся в парамерт network_names

    Обратно возвращается тот же словарь, но с дополненными названиями
    {'network_names': ['ETH', 'ETH2', 'ERC20'], 'fee': 0.001, 'withdraw_min': 0.01}
    """

    dict_with_network = dict_with_network.copy()
    for network_name in dict_with_network['network_names']:
        for list_networks_name in list_matching_networks:
            if network_name in list_networks_name:
                for additional_network_name in list_networks_name:
                    if additional_network_name not in dict_with_network['network_names']:
                        dict_with_network['network_names'].append(additional_network_name)

    return dict_with_network



dict_with_network = {'network_names': ['ETH', 'ETH2'], 'fee': 0.001, 'withdraw_min': 0.01}
list_matching_networks = [['BEP20(BSC)', 'BSC'], ['ERC20', 'ETH', 'BLA']]

res = _add_additional_network_names_to_the_list_of_names(dict_with_network, list_matching_networks)
print(res)