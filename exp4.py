import requests

def _check_coin_in_list_not_support(coin, list_exchange_not_support):
    """
    Проверяет, есть ли монтеа в списке неподдерживаемых моенет.
    :return True - если монета есть в списке неподдерживаемых монет.
    """
    return any(coin.lower() == s.lower() for s in list_exchange_not_support)









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
                if response_json['label'] != "INVALID_CURRENCY":
                    text = f"-------------------------------\n" \
                           f"Ошибка при получении данных (не 200): {response.text}\n" \
                           f"биржа: {stock_market}" \
                           f"монета: {currency}"
                    print(text)

        except Exception as e:
            text = f'При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n'
            print(text)

    return orders_sell, orders_buy








currencies = ['btc', 'doge', 'ltc', 'CCD', 'TOP', 'METAL', 'COTI', 'RIBBIT', 'TRVL', 'EMON', 'KOK', 'REEF', 'REELT', 'CVTX', 'WAS',
                'HAPI', 'MOON', 'CNAME', 'VOLT', 'LGX', 'GPT', 'TSUKA', 'UNB', 'XEN', 'KON', 'DAO', 'ORBS', 'WMT', 'AFC', 'CRO', 'DPR', 'SQUAD',
                'CHRP', 'PRX', 'MCRT', 'HYDRA', 'EGAME', 'POOLX', 'MPLX', 'RAIN', 'TABOO', 'ML', 'DEUS', 'FITFI', 'AICODE', 'VELO', 'DZOO',
                'MBX', 'SPA', 'LBLOCK', 'FLR', 'LOOP', 'OPTIMUS', 'ETHF', 'STND', 'AZERO', 'BONK', 'BOB', 'BAX', 'XPRT', 'RLTM', 'MESA', 'PRIMAL',
                'EJS', 'FBX', 'RLTM', 'PIG', 'ITSB', 'AFC', 'VPAD', 'XETA', 'WNXM', 'MTA', 'TEL', 'PIG', 'POOH', 'IMGNAI', 'DINO', 'TLOS', 'CEUR',
                'FLOKICEO', 'TORN', 'VGX', 'POLC']

list_exchange_not_support = []
for currency in currencies:
    a, b = _get_orders_from_gate(currency, list_exchange_not_support)
    print(a)
    print(b)
    print('--------')
