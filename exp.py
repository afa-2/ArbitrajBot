import requests
import logging


def _get_orders_from_gate(currency):
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

    try:
        # Отправка запроса к API
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code != 200:
            text = f"Ошибка при получении данных: {response.text}"
            logging.error(text)
            print(text)

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

        return orders_sell, orders_buy

    except Exception as e:
        text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'
        logging.error(text)
        print(text)

orders_sell, orders_buy = _get_orders_from_gate('btc')
print(orders_sell)
print(orders_buy)