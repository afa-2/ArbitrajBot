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



def _get_orders_from_kucoin(currency):
    """
    Функция для получения всех ордеров на продажу и покупку переданной валюты с биржи www.bybit.com.
    :param symbol: Символ валюты.
    :return: Список ордеров на продажу.
    """
    stock_market = 'kucoin'
    link_currency_pair = f'https://www.kucoin.com/ru/trade/{currency}-USDT'

    symbol = currency.upper() + '-USDT'
    # URL для получения стакана заявок (order book)
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={symbol}"

    orders_buy = []
    orders_sell = []

    try:
        # Отправка запроса к API Bybit
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении данных: {response.text}")

        # Получение стакана заявок (order book)
        order_book = response.json()

        # Фильтрация ордеров на продажу и покупку
        data = order_book['data']
        for order_buy in data['asks']:
            orders_buy.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                               'price': order_buy[0], 'quantity': order_buy[1]})

        for order_sell in data['bids']:
            orders_sell.append({'stock_market': stock_market, 'link_currency_pair': link_currency_pair, 'symbol': symbol,
                               'price': order_sell[0], 'quantity': order_sell[1]})

        return orders_buy, orders_sell

    except Exception as e:
        print('При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}')

orders_buy, orders_sell = _get_orders_from_bybit('BTC')
print(orders_buy)
print(orders_sell)

print('-----------------------------------------')

orders_buy, orders_sell = _get_orders_from_kucoin('BTC')
print(orders_buy)
print(orders_sell)