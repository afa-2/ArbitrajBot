import requests

def _check_coin_in_list_not_support(coin, list_exchange_not_support):
    """
    Проверяет, есть ли монтеа в списке неподдерживаемых моенет.
    :return True - если монета есть в списке неподдерживаемых монет.
    """
    return any(coin.lower() == s.lower() for s in list_exchange_not_support)









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
                text = f"--------------------------------------------------------------------------------\n" \
                       f"Ошибка при получении данных (не 200): {response.text}\n" \
                       f"биржа: {stock_market}\n" \
                       f"монета: {currency}" \
                       f"--------------------------------------------------------------------------------"
                print(text)

        except Exception as e:
            if response.json()['code'] != 30014:
                text = f'--------------------------------------------------------------------------------\n' \
                       f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                       f'response: {response}\n' \
                       f'response.json: {dict_with_orders}\n' \
                       f'--------------------------------------------------------------------------------'
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
    a, b = _get_orders_from_mexc(currency, list_exchange_not_support)
    print(a)
    print(b)
    print('--------')
