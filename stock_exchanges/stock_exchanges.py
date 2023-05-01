"""
Это раздел для работы с биржами. Здесь функции, которые подключаются к биржам и возращают инфу
"""

import requests


def _get_orders_from_bybit(currency):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.bybit.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    stock_market = 'bybit'
    link_currency_pair = f'https://www.bybit.com/ru-RU/trade/spot/{currency}/USDT'
    symbol = currency.upper() + 'USDT'
    # URL для получения стакана заявок (order book)
    url = "https://api.bybit.com/v2/public/orderBook/L2"

    orders_buy = []
    orders_sell = []

    try:
        # Отправка запроса к API Bybit
        response = requests.get(url, params={"symbol": symbol})

        # Проверка статуса ответа
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении данных: {response.text}")

        # Получение стакана заявок (order book)
        order_book = response.json()

        # Фильтрация ордеров на продажу и покупку
        for order in order_book["result"]:
            if order['side'] == "Sell":
                orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': order['price'], 'quantity': order['size']})
            elif order['side'] == "Buy":
                orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair,  'symbol':symbol, 'price': order['price'], 'quantity': order['size']})

        return orders_buy, orders_sell

    except Exception as e:
        print('При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}')


def _get_orders_from_mexc(currency):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.mexc.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """

    stock_market = 'mexc'
    symbol = currency.lower() + '_usdt'
    base_url = "https://www.mexc.com"
    link_currency_pair = f'https://www.mexc.com/ru-RU/exchange/{currency}_USDT'
    endpoint = "/open/api/v2/market/depth"
    url = base_url + endpoint
    depth = 20  # глубина

    orders_buy = []
    orders_sell = []

    params = {
        "symbol": symbol,
        "depth": depth
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            dict_with_orders = response.json()

            # обрабатываем ордера на продажу
            for order in dict_with_orders["data"]["asks"]:
                orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': order['price'], 'quantity': order['quantity']})

            # обрабатываем ордера на покупку
            for order in dict_with_orders["data"]["bids"]:
                orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol':symbol, 'price': order['price'], 'quantity': order['quantity']})

            return orders_buy, orders_sell

        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        print('При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}')


def all_list_from_all_stock_market(currency: str) -> list:
    """
    Функция принимает валюту,
    затем вызывает все функции для получения данных со всех бирж поочереди в отношении этой валюты
    затем добавляет все полученные массивы в один единый масив, и возвращает его.
    :param currency: валюта
    :return: Возвращает примерно такое: [[ордера на продажу, ордера на покупку], [оредра на продажу, ордера на покупку]]
    """
    all_list_from_all_stock_market = []

    try:
        # биржа www.bybit.com
        orders_buy_from_bybit, orders_sell_from_bybit = _get_orders_from_bybit(currency)
        all_list_from_all_stock_market.append([orders_buy_from_bybit, orders_sell_from_bybit])

        # биржа www.mexc.com
        orders_buy_from_bybit, orders_sell_from_bybit = _get_orders_from_mexc(currency)
        all_list_from_all_stock_market.append([orders_buy_from_bybit, orders_sell_from_bybit])

    except Exception as e:
        print(f'При выполнении функции, получающей данные со всех бирж и объединяющей эти данные в единый массив, произошла ошибка: {e}')

    return all_list_from_all_stock_market

