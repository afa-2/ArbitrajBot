import requests


def _check_coin_in_list_not_support(coin, list_exchange_not_support):
    """
    Проверяет, есть ли монтеа в списке неподдерживаемых моенет.
    :return True - если монета есть в списке неподдерживаемых монет.
    """
    return False


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
        try:
            # Отправка запроса к API
            response = requests.get(url)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Получение стакана заявок (order book)
                order_book = response.json()
                _save_text_to_file(order_book, 'gate.txt', symbol)
                # Фильтрация ордеров на продажу и покупку
                data = order_book['data']
                print(data)
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

        except Exception as e:
            text = 'При работе функции, получающей данные с ' + stock_market + f' произошла ошибка: {e}'

    return orders_sell, orders_buy

list_exchange_not_support = []
a, b = _get_orders_from_bitget('btc', list_exchange_not_support)
print(a)
print(b)