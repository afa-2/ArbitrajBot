"""
Это раздел для работы с биржами. Здесь функции, которые подключаются к биржам и возращают инфу
"""
import requests
import logging
import configparser
import datetime


def _save_text_to_file(text, file, coin):
    """
    Функция, для сохранения записей в его конкретный файл
    """
    pass
    # current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    # with open(file, "a") as file:
    #     text = f'{current_time}\n' \
    #            f'{coin}' \
    #            f' {text}\n\n'
    #     file.write(f"{current_time} {text}\n")


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
        try:
            # Отправка запроса к API Bybit
            response = requests.get(url, params={"symbol": symbol})

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'bybit.txt', symbol)

                # Фильтрация ордеров на продажу и покупку
                for order in order_book["result"]:
                    if order['side'] == "Sell":
                        orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['size'])})
                    elif order['side'] == "Buy":
                        orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['size'])})

            else:
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
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
        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                dict_with_orders = response.json()
                _save_text_to_file(dict_with_orders, 'mexc.txt', symbol)
                # обрабатываем ордера на продажу
                for order in dict_with_orders["data"]["asks"]:
                    orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['quantity'])})

                # обрабатываем ордера на покупку
                for order in dict_with_orders["data"]["bids"]:
                    orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': float(order['price']), 'quantity': float(order['quantity'])})

            else:
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
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
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'kucoin.txt', symbol)

                # Фильтрация ордеров на продажу и покупку
                data = order_book['data']
                for order_sell in data['asks']:
                    orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                for order_buy in data['bids']:
                    orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_buy[0]), 'quantity': float(order_buy[1])})

            else:
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
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

    orders_buy = []
    orders_sell = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'binance.txt', symbol)

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
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
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
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'huobi.txt', symbol)
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
                    text = 'упс, ошибочка', order_book
                    logging.error(text)

            else:
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
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
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'gate.txt', symbol)
                # Фильтрация ордеров на продажу и покупку
                data = order_book
                for order_sell in data['asks']:
                    orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_sell[0]), 'quantity': float(order_sell[1])})

                for order_buy in data['bids']:
                    orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                                       'price': float(order_buy[0]), 'quantity': float(order_buy[1])})

            else:
                text = f"-------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}" \
                       f"монета: {currency}"
                logging.error(text)

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
            logging.error(text)

    return orders_sell, orders_buy


def all_list_from_all_stock_market(currency: str) -> list:
    """
    Функция принимает валюту,
    затем вызывает все функции для получения данных со всех бирж поочереди в отношении этой валюты
    затем добавляет все полученные массивы в один единый масив, и возвращает его.
    :param currency: валюта
    :return: Возвращает примерно такое: [[ордера на продажу, ордера на покупку], [оредра на продажу, ордера на покупку]]
    """
    all_list_from_all_stock_market = []

    # формируем словарь со списком, какие биржи, что не поддерживают
    config = configparser.ConfigParser()
    config.read('config.ini')
    dict_exchange_not_support = {}
    for exchange in ['bybit', 'mexc', 'kucoin', 'binance', 'huobi', 'gate']:
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

    except Exception as e:
        text = f'При выполнении функции, получающей данные со всех бирж и объединяющей эти данные в единый массив, произошла ошибка: {e}'
        logging.error(text)

    _save_text_to_file(all_list_from_all_stock_market, 'all_list_from_all_stock_market.txt', currency)
    return all_list_from_all_stock_market





