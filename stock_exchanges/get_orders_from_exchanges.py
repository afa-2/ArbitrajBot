"""
Это раздел для работы с биржами. Здесь функции, которые подключаются к биржам и возращают инфу
"""
import requests
import logging
import configparser
import datetime


def _check_coin_in_list_not_support(coin, list_exchange_not_support):
    """
    Проверяет, есть ли монтеа в списке неподдерживаемых моенет.
    :return True - если монета есть в списке неподдерживаемых монет.
    """
    return any(coin.lower() == s.lower() for s in list_exchange_not_support)


def _get_orders_from_bybit(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.bybit.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу и список ордеров на покупку.
    """
    stock_market = 'bybit'
    link_currency_pair = f'https://www.bybit.com/ru-RU/trade/spot/{currency}/USDT'
    symbol = currency.upper() + 'USDT'
    # URL для получения стакана заявок (order book)
    url = "https://api.bybit.com/v2/public/orderBook/L2"

    orders_buy = []
    orders_sell = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API Bybit
            response = requests.get(url, params={"symbol": symbol})

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                # Фильтрация ордеров на продажу и покупку
                for order in order_book["result"]:
                    if order['side'] == "Sell":
                        orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['size'])})
                    elif order['side'] == "Buy":
                        orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['size'])})

            else:
                text = f"--------------------------------------------------------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}\n" \
                       f"монета: {currency}" \
                       f"--------------------------------------------------------------------------------"
                logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_mexc(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.mexc.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу и список ордеров на покупку.
    """

    stock_market = 'mexc'
    symbol = currency.lower() + '_usdt'
    base_url = "https://www.mexc.com"
    endpoint = "/open/api/v2/market/depth"
    link_currency_pair = f'https://www.mexc.com/ru-RU/exchange/{currency}_USDT'
    url = base_url + endpoint
    depth = 20  # глубина

    orders_buy = []
    orders_sell = []

    params = {
        "symbol": symbol,
        "depth": depth
    }

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        dict_with_orders = ''
        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                dict_with_orders = response.json()
                # обрабатываем ордера на продажу
                for order in dict_with_orders["data"]["asks"]:
                    orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['quantity'])})

                # обрабатываем ордера на покупку
                for order in dict_with_orders["data"]["bids"]:
                    orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['quantity'])})

            else:
                if response.json()['code'] != 30014:
                    text = f"--------------------------------------------------------------------------------\n" \
                           f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                           f"биржа: {stock_market}\n" \
                           f"монета: {currency}" \
                           f"--------------------------------------------------------------------------------"
                    logging.error(text)

        except Exception as e:
                text = f'--------------------------------------------------------------------------------\n' \
                       f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                       f'response: {response}\n' \
                       f'response.json: {dict_with_orders}\n' \
                       f'--------------------------------------------------------------------------------'
                logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_kucoin(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.kucoin.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    currency = currency.upper()
    stock_market = 'kucoin'
    link_currency_pair = f'https://www.kucoin.com/ru/trade/{currency}-USDT'
    symbol = currency + '-USDT'
    # URL для получения стакана заявок (order book)
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={symbol}"

    orders_buy = []
    orders_sell = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                # Фильтрация ордеров на продажу и покупку
                data = order_book['data']
                if data['asks'] != None:
                    for order_sell in data['asks']:
                        orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                if data['bids'] != None:
                    for order_buy in data['bids']:
                        orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_buy[0]), 'quantity': float(order_buy[1])})

            else:
                text = f"--------------------------------------------------------------------------------\n" \
                       f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                       f"биржа: {stock_market}\n" \
                       f"монета: {currency}\n" \
                       f"--------------------------------------------------------------------------------"
                logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_binance(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.binance.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    currency = currency.upper()
    stock_market = 'binance'
    link_currency_pair = f'https://www.binance.com/ru/trade/{currency}_USDT'
    symbol = currency + 'USDT'
    # URL для получения стакана заявок (order book)
    url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit=20'
    list_msg_ignore = []

    orders_buy = []
    orders_sell = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                # Фильтрация ордеров на продажу и покупку
                data = order_book
                for order_sell in data['asks']:
                    orders_sell.append(
                        {'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                         'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                for order_buy in data['bids']:
                    orders_buy.append(
                        {'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                         'price': float(order_buy[0]), 'quantity': float(order_buy[1])})
            else:
                response_json = response.json()
                if response_json['msg'] != "Invalid symbol.":
                    text = f"--------------------------------------------------------------------------------\n" \
                           f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                           f"биржа: {stock_market}\n" \
                           f"монета: {currency}\n" \
                           f"--------------------------------------------------------------------------------"
                    logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_huobi(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.huobi.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    currency = currency.lower()
    stock_market = 'huobi'
    link_currency_pair = f'https://www.huobi.com/ru-ru/trade/{currency}_usdt'
    symbol = currency + 'usdt'
    # URL для получения стакана заявок (order book)
    url = f'https://api.huobi.pro/market/depth?symbol={symbol}&type=step0'

    orders_buy = []
    orders_sell = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                if order_book['status'] != 'error':
                    # Фильтрация ордеров на продажу и покупку
                    data = order_book['tick']
                    for order_sell in data['asks']:
                        orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                    for order_buy in data['bids']:
                        orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_buy[0]), 'quantity': float(order_buy[1])})
                else:
                    if response.json()['err-msg'] != "invalid symbol":
                        text = f"--------------------------------------------------------------------------------\n" \
                               f"Ответ успешно получен (статус 200), но ошибка (status error = error).\n " \
                               f"response.text: {response.text}\n" \
                               f"биржа: {stock_market}\n" \
                               f"монета: {currency}\n" \
                               f"--------------------------------------------------------------------------------"
                        logging.error(text)

            else:
                text = f"--------------------------------------------------------------------------------\n" \
                       f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                       f"биржа: {stock_market}\n" \
                       f"монета: {currency}\n" \
                       f"--------------------------------------------------------------------------------"
                logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_gate(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.gate.io.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    currency = currency.upper()
    stock_market = 'gate'
    link_currency_pair = f'https://www.gate.io/ru/trade/{currency}_USDT'
    symbol = currency + '_USDT'
    # URL для получения стакана заявок (order book)
    url = f'https://api.gateio.ws/api/v4/spot/order_book?currency_pair={symbol}&limit=20'

    orders_sell = []
    orders_buy = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''

        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                # Фильтрация ордеров на продажу и покупку
                data = order_book
                for order_sell in data['asks']:
                    orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                for order_buy in data['bids']:
                    orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_buy[0]), 'quantity': float(order_buy[1])})

            else:
                response_json = response.json()
                list_ignore_label_error = ['INVALID_CURRENCY', 'INVALID_CURRENCY_PAIR']
                if response_json['label'] not in list_ignore_label_error:
                    text = f"--------------------------------------------------------------------------------\n" \
                           f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                           f"биржа: {stock_market}\n" \
                           f"монета: {currency}\n" \
                           f"--------------------------------------------------------------------------------"
                    logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def _get_orders_from_bitget(currency, list_exchange_not_support):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи bitget.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    currency = currency.upper()
    stock_market = 'bitget'
    link_currency_pair = f'https://www.bitget.com/ru/spot/{currency}USDT_SPBL?type=spot'

    currency = currency.lower()
    symbol = currency + '_usdt'
    # URL для получения стакана заявок (order book)
    url = f'https://api.bitget.com/data/v1/market/depth?symbol={symbol}'

    orders_sell = []
    orders_buy = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()

                # Фильтрация ордеров на продажу и покупку
                data = order_book['data']
                if data['asks'] != None:
                    for order_sell in data['asks']:
                        orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                if data['bids'] != None:
                    for order_buy in data['bids']:
                        orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                           'price': float(order_buy[0]), 'quantity': float(order_buy[1])})

            else:
                if response.json()['code'] != '40019':
                    text = f"--------------------------------------------------------------------------------\n" \
                           f"Ошибка при получении данных (Ответ не 200): {response.text}\n" \
                           f"биржа: {stock_market}\n" \
                           f"монета: {currency}\n" \
                           f"--------------------------------------------------------------------------------"
                    logging.error(text)

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            logging.error(text)

    return orders_sell, orders_buy


def all_list_from_all_stock_market(currency: str) -> list:
    """
    Функция принимает валюту,
    затем вызывает все функции для получения данных со всех бирж поочереди в отношении этой валюты
    затем добавляет все полученные массивы в один единый массив, и возвращает его.
    :param currency: валюта
    :return: Возвращает примерно такое:
    [[[{биржа1, ордер на продажу}, {биржа1, ордер на продажу}], [{биржа1, ордер на покупку, ордера на покупку}]],
    [[{биржа2, ордер на продажу}, {биржа2, ордер на продажу}], [{биржа2, ордер на покупку, ордера на покупку}]]

    Пример возврата:
    [
     [
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.6, 'quantity': 0.772},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.7, 'quantity': 0.001},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.8, 'quantity': 0.001}, }
      ],
      [
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.5, 'quantity': 24.364},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28893.4, 'quantity': 0.074},
       {'stock_market': 'bybit', 'link_currency_pair': 'https://www.bybit.com/ru-RU/trade/spot/btc/USDT', 'symbol': 'BTCUSDT', 'price': 28892.9, 'quantity': 0.447}
      ]
     ],
     [
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.47, 'quantity': 4.574974},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.63, 'quantity': 4.416018},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.66, 'quantity': 2.384561}
      ],
      [
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.46, 'quantity': 1.6985},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.45, 'quantity': 4.492647},
       {'stock_market': 'mexc', 'link_currency_pair': 'https://www.mexc.com/ru-RU/exchange/btc_USDT', 'symbol': 'btc_usdt', 'price': 28914.41, 'quantity': 2.972827}
      ]
     ]
    ]
    """
    all_list_from_all_stock_market = []

    # формируем словарь со списком, какие биржи, что не поддерживают
    config = configparser.ConfigParser()
    config.read('config.ini')
    dict_exchange_not_support = {}
    for exchange in ['bybit', 'mexc', 'kucoin', 'binance', 'huobi', 'gate', 'bitget']:
        string = exchange + '_not_support'
        exchange_not_support = config.get('settings', string).strip().lower()
        dict_exchange_not_support[exchange] = exchange_not_support.strip('][').split(', ')

    try:
        # биржа www.bybit.com
        orders_sell_from_bybit, orders_buy_from_bybit = _get_orders_from_bybit(currency, dict_exchange_not_support['bybit'])
        if len(orders_sell_from_bybit) > 0 and len(orders_buy_from_bybit) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_bybit, orders_buy_from_bybit])

        # биржа www.mexc.com
        orders_sell_from_mexc, orders_buy_from_mexc = _get_orders_from_mexc(currency, dict_exchange_not_support['mexc'])
        if len(orders_sell_from_mexc) > 0 and len(orders_buy_from_mexc) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_mexc, orders_buy_from_mexc])

        # биржа www.kucoin.com
        orders_sell_from_kucoin, orders_buy_from_kucoin = _get_orders_from_kucoin(currency, dict_exchange_not_support['kucoin'])
        if len(orders_sell_from_kucoin) > 0 and len(orders_buy_from_kucoin) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_kucoin, orders_buy_from_kucoin])

        # биржа www.binance.com
        orders_sell_from_binance, orders_buy_from_binance = _get_orders_from_binance(currency, dict_exchange_not_support['binance'])
        if len(orders_sell_from_binance) > 0 and len(orders_buy_from_binance) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_binance, orders_buy_from_binance])

        # биржа www.huobi.com
        orders_sell_from_huobi, orders_buy_from_huobi = _get_orders_from_huobi(currency, dict_exchange_not_support['huobi'])
        if len(orders_sell_from_huobi) > 0 and len(orders_buy_from_huobi) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_huobi, orders_buy_from_huobi])

        # биржа www.gate.io
        orders_sell_from_gate, orders_buy_from_gate = _get_orders_from_gate(currency, dict_exchange_not_support['gate'])
        if len(orders_sell_from_gate) > 0 and len(orders_buy_from_gate) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_gate, orders_buy_from_gate])

        # биржа bitget.com
        orders_sell_from_bitget, orders_buy_from_bitget = _get_orders_from_bitget(currency, dict_exchange_not_support['bitget'])
        if len(orders_sell_from_bitget) > 0 and len(orders_buy_from_bitget) > 0:
            all_list_from_all_stock_market.append([orders_sell_from_bitget, orders_buy_from_bitget])

    except Exception as e:
        text = f'При выполнении функции, получающей данные со всех бирж и объединяющей эти данные в единый массив, произошла ошибка: {e}' \
               f'all_list_from_all_stock_market: {all_list_from_all_stock_market}'
        logging.error(text)

    return all_list_from_all_stock_market





