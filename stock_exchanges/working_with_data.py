import logging


def _searching_currency_differences(list_with_orders_from_all_stock_market: list) -> list:
    """
    Функция ищет релевантные предложения, где цена в ордере на продажу с одной биржи больше цены ордера на покупку
    с другой биржи и соединяет такие совпадения в массив словарей:
    [{order_buy: [биржа, ссылка, цена], orders_sell: [биржа, ссылка, цена], [биржа, ссылка, цена], [биржа, ссылка, цена]},
    {order_buy: [биржа, ссылка, цена], orders_sell: [биржа, ссылка, цена], [биржа, ссылка, цена], [биржа, ссылка, цена]}]

    Получаем:
    Получаем список с ордерами на покупку и продажу со всех бирж, примерно такое:
    [[[{биржа1, ордер на продажу}, {биржа1, ордер на продажу}], [{биржа1, ордер на покупку, ордера на покупку}]],
    [[{биржа2, ордер на продажу}, {биржа2, ордер на продажу}], [{биржа2, ордер на покупку, ордера на покупку}]]

    Пример:
    [
     [
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.6, 'quantity': 0.772},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.7, 'quantity': 0.001},
      ],
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.5, 'quantity': 24.364},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.4, 'quantity': 0.074},
      ]
     ],
     [
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.47, 'quantity': 4.574974},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.63, 'quantity': 4.416018},
      ],
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.46, 'quantity': 1.6985},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.45, 'quantity': 4.492647},
      ]
     ]
    ]

    Принцип работы.
    Получаем список с ордерами со всех бирж.
    В отношении каждой пары бирж (например, биржа 1 и биржа 2), берем каждый ордер на покупку с биржи 1 и берем
    все ордера на продажу с биржи 2
    Сравниваем, если цена из ордера на продажу больше цены из ордера на покупку (т.е. кто-то готов купить за 100usd,
    а кто-то готов продать за 95usd, то тогда эту пару вносит в финальный список order_sell_and_orders_by.

    Возвращает словарь с order_sell (ордер на покупку) и orders_buy (список ордеров на продажу), которые по стоимости
    ниже ордера на покупку. Т.е. возвращаем отфильтрованные ордеры.
    Пример возврата:
    [
     {'order_buy': ['mexc', 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'btc_usdt', 28832.78, 4.81299],
      'orders_sell': [
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28805.0, 10.641],
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28805.8, 0.033],
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28806.0, 0.014]
      ]
     },
     {'order_buy': ['mexc', 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'btc_usdt', 28832.77, 0.723388],
      'orders_sell': [
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28805.0, 10.641],
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28805.8, 0.033],
       ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28806.0, 0.014],
      ]
     }
    ]
    """
    liet_orders_buy_with_orders_sell = []  # список, одер о готовности купить и к нему ордера о готовности продать

    for stock_market_one in list_with_orders_from_all_stock_market:  # в отношении каждой биржи
        for stock_market_two in list_with_orders_from_all_stock_market:  # в отношении кажой биржи 2, что бы сравнивать (биржа 1 и биржа 2)
            if stock_market_one != stock_market_two:
                all_orders_buy_from_stock_market_one = stock_market_one[1][:3]  # получаем все ордеры на покупку с биржи 1
                all_orders_sell_from_stock_market_two = stock_market_two[0]  # получаем все ордеры на продажу с биржи 2

                first_price_order_buy_from_market_one = all_orders_buy_from_stock_market_one[0]['price']  # ордера на покупку с биржи 1, первое значение цены
                first_price_order_sell_from_market_two = all_orders_sell_from_stock_market_two[0]['price']  # ордера на продажу с биржи 2, первое значение цены

                if first_price_order_buy_from_market_one > first_price_order_sell_from_market_two:  # если максимальная цена предложения о покупке больше чем минимаьная цена предложения о продаже
                    for order_buy in all_orders_buy_from_stock_market_one:  # в отношении каждого ордера о готовности купить (ордера на продажу)
                        order_buy_market = order_buy['stock_market']
                        order_buy_link_currency_pair = order_buy['link_currency_pair']
                        order_buy_symbol = order_buy['symbol']
                        order_buy_price = order_buy['price']
                        order_buy_quantity = order_buy['quantity']

                        orders_sell = []
                        for order_sell in all_orders_sell_from_stock_market_two:  # в отношении каждого ордера о готовности продать
                            order_sell_market = order_sell['stock_market']
                            order_sell_link_currency_pair = order_sell['link_currency_pair']
                            order_sell_symbol = order_sell['symbol']
                            order_sell_price = order_sell['price']
                            order_sell_quantity = order_sell['quantity']

                            if order_buy_price > order_sell_price:  # если цена ордера на покупку больше цены ордера на продажу
                                # добавляем все в список
                                orders_sell.append([order_sell_market, order_sell_link_currency_pair, order_sell_price, order_sell_quantity])

                        if len(orders_sell) > 0:
                            order_buy_and_orders_sell = {}
                            order_buy_and_orders_sell['order_buy'] = [order_buy_market, order_buy_link_currency_pair, order_buy_symbol, order_buy_price, order_buy_quantity]
                            order_buy_and_orders_sell['orders_sell'] = orders_sell
                            liet_orders_buy_with_orders_sell.append(order_buy_and_orders_sell)

    return liet_orders_buy_with_orders_sell


def return_networks_for_exchange_and_coin(dict_with_networks: dict, name_exchange: str, coin: str):
    """
    Функция принимает словарь с сетями, название биржи и название монеты. Находит в словаре сети, отнсящиеся к этой
    бирже и к этой монете и возвращает список сетей.

    Пример возврата:
        [{'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.001, 'withdraw_min': 0.01},
        {'network_names': ['ERC20', 'ETH'], 'fee': 0.005, 'withdraw_min': 0.01},
        {'network_names': ['KCC', 'KCC'], 'fee': 0.0002, 'withdraw_min': 0.01},
        {'network_names': ['TRC20', 'TRX'], 'fee': 0.0005, 'withdraw_min': 0.002},
        {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.001, 'withdraw_min': 0.001}]
    """
    networks = {}
    if name_exchange in dict_with_networks:
        if coin in dict_with_networks[name_exchange]:
            networks = dict_with_networks[name_exchange][coin].copy()

    return networks


def _search_matching_networks(dict_with_networks: dict, name_exchange_1: str, name_exchange_2: str, coin: str) -> list:
    """
    Получаем
    1) словарь следующего вида (dict_with_networks):
    {'last_update': datetime.datetime(2023, 6, 21, 16, 8, 47, 390196),
    'bybit': {'BTC':
                 {'BTC': {'fee': 0.0003, 'withdraw_min': 0.001, 'percentage_fee': 0},
                 'BEP20(BSC)': {'fee': 1e-05, 'withdraw_min': 0.0001, 'percentage_fee': 0},
                 'TRC20': {'fee': 0.0001, 'withdraw_min': 0.001, 'percentage_fee': 0}},
             'DOGE': {'DOGE': {'fee': 5.0, 'withdraw_min': 25.0, 'percentage_fee': 0.0}},
             'LTC': {'LTC': {'fee': 0.001, 'withdraw_min': 0.1, 'percentage_fee': 0.0}}},
    'mexc': {'BTC':
             {'BTC': {'fee': 0.0003, 'withdraw_min': 0.001, 'percentage_fee': 0},
             'BEP20(BSC)': {'fee': 1e-05, 'withdraw_min': 0.0001, 'percentage_fee': 0},
             'TRC20': {'fee': 0.0001, 'withdraw_min': 0.001, 'percentage_fee': 0}},
         'DOGE': {'DOGE': {'fee': 5.0, 'withdraw_min': 25.0, 'percentage_fee': 0.0}},
         'LTC': {'LTC': {'fee': 0.001, 'withdraw_min': 0.1, 'percentage_fee': 0.0}}},
    }

    {'last_update': datetime.datetime(2023, 6, 21, 16, 8, 47, 390196),
    'bybit': {'BTC': [{'network_names': ['BTC'], 'fee': 0.0005, 'withdraw_min': 0.002},
                    {'network_names': ['BEP20'], 'fee': 5.1e-06, 'withdraw_min': 7.8e-06}],
            'USDT': [{'network_names': ['OMNI'], 'fee': 15.0, 'withdraw_min': 100.0},
                    {'network_names': ['ERC20'], 'fee': 3.0638816, 'withdraw_min': 1.0},
                    {'network_names': ['BTTC'], 'fee': 1.0, 'withdraw_min': 1.0}],
            'ETH': [{'network_names': ['ARBITRUMNOVA'], 'fee': 0.1, 'withdraw_min': 10.0},
                    {'network_names': ['ARBITRUMONE'], 'fee': 0.0001, 'withdraw_min': 0.0008},
                    {'network_names': ['BEP20'], 'fee': 8e-05, 'withdraw_min': 0.00011}]},
    'mexc': {'BTC': [{'network_names': ['BTC'], 'fee': 0.0005, 'withdraw_min': 0.002},
                    {'network_names': ['BEP20'], 'fee': 5.1e-06, 'withdraw_min': 7.8e-06}],
            'USDT': [{'network_names': ['OMNI'], 'fee': 15.0, 'withdraw_min': 100.0},
                    {'network_names': ['ERC20'], 'fee': 3.0638816, 'withdraw_min': 1.0},
                    {'network_names': ['BTTC'], 'fee': 1.0, 'withdraw_min': 1.0}],
            'ETH': [{'network_names': ['ARBITRUMNOVA'], 'fee': 0.1, 'withdraw_min': 10.0},
                    {'network_names': ['ARBITRUMONE'], 'fee': 0.0001, 'withdraw_min': 0.0008},
                    {'network_names': ['BEP20'], 'fee': 8e-05, 'withdraw_min': 0.00011}]},
    }

    2) Биржа 1
    3) Биржа 2
    4) Название валюты

    Ищем совпадения валют в словаре с биржами. Возвращаем список с совпадениями валют.

    Пример возврата:
    [{'network_names': ['ERC20', 'ETH'], 'fee': 0.004}, {'network_names': ['KCC', 'DHDF', 'VBFGN'], 'fee': 0.0005}]
    """
    coin = coin.upper()
    name_exchange_1 = name_exchange_1.lower()
    name_exchange_2 = name_exchange_2.lower()

    # сети биржи 1
    networks_on_exchange_1 = return_networks_for_exchange_and_coin(dict_with_networks, name_exchange_1, coin)
    # сети с биржи 2
    networks_on_exchange_2 = return_networks_for_exchange_and_coin(dict_with_networks, name_exchange_2, coin)

    # [{'network_names': ['OPTIMISM', 'OPTIMISM'], 'fee': 0.001, 'withdraw_min': 0.01},
    #  {'network_names': ['ERC20', 'ETH'], 'fee': 0.005, 'withdraw_min': 0.01},
    #  {'network_names': ['KCC', 'KCC'], 'fee': 0.0002, 'withdraw_min': 0.01},
    #  {'network_names': ['TRC20', 'TRX'], 'fee': 0.0005, 'withdraw_min': 0.002},
    #  {'network_names': ['ARBITRUM', 'ARBITRUM'], 'fee': 0.001, 'withdraw_min': 0.001}]

    #  ищем совпадения по сетям и подбираем самую выгодную
    list_networks_matches = []  # список совпадающих сетей

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

    return list_networks_matches


def _calculate_margin_filter_order(order_buy_and_orders_sell: dict, dict_with_networks: dict) -> dict:
    """
    Получаем ордер на покупку и список ордеров на продажу (
    Например:
    ['mexc', 'https://www.mexc.com/ru-RU/exchange/BTC_USDT', 'btc_usdt', '27011.11', '3.5616',
        [['bybit', 'https://www.bybit.com/ru-RU/trade/spot/BTC/USDT', '27005.1', 45.494],
         ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/BTC/USDT', '27005.3', 0.3]
        ]
    )
    Считаем маржу в процентах и долларах и отсеиваем лишние ордера
    Принцип работы:
    берем необходимое количество монет из ордера на продажу и берем столько ордеров на продажу, что бы перекрывало потребность,
    остальные ордера отсеиываем.

    Считаем маржу в процентах и в долларах
    :return: Возвращаем
    """
    dict_with_result = {}
    dict_with_result['order_buy'] = []
    dict_with_result['orders_sell'] = []

    presumably_spent = 0  # предположительно потратили
    presumably_bought = 0  # предположительно куплено монет

    order_buy = order_buy_and_orders_sell['order_buy']  # ордер на покупку
    dict_with_result['order_buy'] = order_buy
    name_exchange_where_buy = order_buy[0]  # название биржи, на которой надо купить
    name_coin = order_buy[2]  # название монеты
    name_coin = name_coin.upper()  # переводим в верхний регистр
    name_coin = name_coin.replace('_USDT', '')  # убираем нижнее подчеркивание и usdt

    price_order_buy = float(order_buy[3])  # цена одной монеты в ордере на покупку
    quantity_order_buy = float(order_buy[4])  # количество монет в ордере на покупку

    orders_sell = order_buy_and_orders_sell['orders_sell']  # ордера на продажу
    name_exchange_where_sell = orders_sell[0][0]  # название биржи, на которой надо продать

    # считаем сколько нам надо ордеров на продажу, что бы покрыть потребности в ордере на покупку, остальное отсеиваем
    for order_sell in orders_sell:  # в отношении каждого ордера на продажу
        price_order_sell = float(order_sell[2])  # цена одной монеты в ордере на продажу
        quantity_order_sell = float(order_sell[3])  # количество монет в ордере на продажу

        if presumably_bought + quantity_order_sell <= quantity_order_buy:  # если предположительно куплено монет + количество монет в ордере на продажу меньше или равно количеству монет в ордере на покупку
            presumably_bought += quantity_order_sell  # прибавляем к предположительно купленным монетам количество монет в ордере на продажу
            presumably_spent += quantity_order_sell * price_order_sell  # прибавляем к предположительно потраченным деньгам количество монет в ордере на продажу умноженное на цену ордера на продажу
            dict_with_result['orders_sell'].append(order_sell)  # добавляем ордер на продажу в список

        else:  # если предположительно куплено монет + количество монет в ордере на продажу больше чем количество монет в ордере на покупку
            we_need = quantity_order_buy - presumably_bought  # вычисляем сколько нам нужно монет, что бы перекрыть потребность
            presumably_bought += we_need  # прибавляем к предположительно купленным монетам количество монет, которое нам нужно
            presumably_spent += we_need * price_order_sell  # прибавляем к предположительно потраченным деньгам количество монет, которое нам нужно умноженное на цену ордера на продажу
            order_sell[3] = we_need  # меняем количество монет в ордере на продажу на количество монет, которое нам нужно
            dict_with_result['orders_sell'].append(order_sell)  # добавляем ордер на продажу в список
            break  # выходим из цикла

    # получаем совпадающие сети в обоих биржах
    dict_with_result['matching_networks'] = []
    list_with_matching_networks = _search_matching_networks(dict_with_networks, name_exchange_where_buy, name_exchange_where_sell, name_coin)
    for matching_networks in list_with_matching_networks:
        dict_with_result['matching_networks'].append(matching_networks.copy())
    # выбираем сеть с самой низкой комиссией
    if len(list_with_matching_networks) > 0:  # если в списке вообще что-нибудь есть
        network_with_min_fee = min(list_with_matching_networks, key=lambda x: x['fee'])
    else: # если в списке ничего нет
        network_with_min_fee = {}

    # если сеть есть, то заносим ее в словарь
    if len(network_with_min_fee) > 0:
        dict_with_result['network_with_min_fee'] = network_with_min_fee
        network_fee = float(network_with_min_fee['fee'])
    else:
        dict_with_result['network_with_min_fee'] = {}
        network_fee = 0

    # комиссия сети в долларах. Курс - стоимость монеты в ордере на покупку
    network_fee_in_dollars = network_fee * price_order_buy
    dict_with_result['network_with_min_fee']['fee_in_dollars'] = network_fee_in_dollars

    # прибавляем к предположительно потраченным деньгам комиссию сети умноженную на цену ордера покупки
    presumably_spent += network_fee_in_dollars

    # считаем маржу в долларах
    # Маржа в долларах: (количество купленных монет * цена монеты в ордере на покупку) - количество потраченных денег
    margin_in_dol = (presumably_bought * price_order_buy) - presumably_spent
    margin_in_dol = round(margin_in_dol, 2)

    # считаем маржу в процентах
    margin = margin_in_dol/presumably_spent * 100
    margin = round(margin, 2)

    dict_with_result['need_spent'] = presumably_spent  # надо потратить
    dict_with_result['need_bought'] = presumably_bought  # надо купить
    dict_with_result['margin'] = margin
    dict_with_result['margin_in_dol'] = margin_in_dol

    return dict_with_result


def data_processing(list_all_list_from_all_stock_market: list, dict_with_networks: dict) -> list:
    """
    Функция обрабатывает "сырые данные". Мы получаем массив с ордерами на продажу и покупку валюты с разных бирж и
    функция обрабатывает этот массив.

    Принимает:
    Получаем список с ордерами на покупку и продажу со всех бирж, примерно такое:
    [[[{биржа1, ордер на продажу}, {биржа1, ордер на продажу}], [{биржа1, ордер на покупку, ордера на покупку}]],
    [[{биржа2, ордер на продажу}, {биржа2, ордер на продажу}], [{биржа2, ордер на покупку, ордера на покупку}]]

    Пример того, что получаем:
    [
     [
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.6, 'quantity': 0.772},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.7, 'quantity': 0.001},
      ],
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.5, 'quantity': 24.364},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.4, 'quantity': 0.074},
      ]
     ],
     [
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.47, 'quantity': 4.574974},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.63, 'quantity': 4.416018},
      ],
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.46, 'quantity': 1.6985},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.45, 'quantity': 4.492647},
      ]
     ]
    ]

    Принцип работы:
    Функция принимает сырые данные, ищет релевантные предложения, где цена в ордере на продажу с одной биржи больше цены
    ордера на покупку с другой биржи и соединяет такие совпадения в массив словарей, далее считает маржу и прочие
    необходимые данные и возвращает массив с релевантными предложениями.

    Возвращает список словарей:
    [
     {'order_buy':
        ['mexc', 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'btc_usdt', 28927.99, 8.866581],
     'orders_sell': [
        ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28914.8, 7.267],
        ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28915.0, 0.001],
        ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28915.5, 1.5985809999999994]],
      'need_spent': 256376.53550549998,
      'need_bought': 8.866581,
      'margin': 0.05,
      'margin_in_dol': 115.83},

      {'order_buy':
         ['mexc', 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'btc_usdt', 28927.94, 5.182642],
      'orders_sell': [
         ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28914.8, 5.182642]],
      'need_spent': 149855.0569016,
      'need_bought': 5.182642,
      'margin': 0.05,
      'margin_in_dol': 68.1},

      {'order_buy':
         ['mexc', 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'btc_usdt', 28927.9, 3.883489],
      'orders_sell': [
         ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 28914.8, 3.883489]],
      'need_spent': 112290.3077372,
      'need_bought': 3.883489,
      'margin': 0.05,
      'margin_in_dol': 50.87}
    ]
    """
    list_of_orders = []  # список словарей, где один словарь это один ордер на покупку и относящиеся к нему ордера на продажу

    # сравниваем все ордеры на покупку со всеми ордерами на продажу. Формируем список словарей, где один словарь
    # это один ордер на покупку и относящиеся к нему ордера на продажу
    orders_sell_and_orders_by = _searching_currency_differences(list_all_list_from_all_stock_market)

    # в отношении каждого ордера на покупку и относящихся к нему ордеров на продажу
    for order_sell_and_orders_by in orders_sell_and_orders_by:
        # считаем маржу в процентах и долларах и отсеиваем лишние ордера
        dict_with_result = _calculate_margin_filter_order(order_sell_and_orders_by, dict_with_networks)
        # добавляем в список ордеров
        list_of_orders.append(dict_with_result)

    return list_of_orders
