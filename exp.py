import configparser
import requests





config = configparser.ConfigParser()
config.read('config.ini')
currencies = config.get('settings', 'currencies').strip()
currencies = currencies.replace(" ", "")
currencies = currencies.replace("\n", "")
currencies = currencies.strip('][').split(',')
# удаляем повторяющиеся валюты
new_list = []
for currency in currencies:
    if currency not in new_list:
        new_list.append(currency)

currencies = new_list






def _check_coin_in_list_not_support(coin, list_exchange_not_support):
    """
    Проверяет, есть ли монтеа в списке неподдерживаемых моенет.
    :return True - если монета есть в списке неподдерживаемых монет.
    """
    return any(coin.lower() == s.lower() for s in list_exchange_not_support)


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
    print(url)

    orders_sell = []
    orders_buy = []

    if not _check_coin_in_list_not_support(currency, list_exchange_not_support):  # если монета не в списке неподдерживаемых монет
        # перетираем значения, что бы если код упал с ошибкой раньше обозначения этих параметров, в лог файл была занесена пустая строка
        response = ''
        order_book = ''
        try:
            # Отправка запроса к API
            response = requests.get(url)
            print(response.json())

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

        except Exception as e:
            text = f'--------------------------------------------------------------------------------\n' \
                   f'Исключение. При работе функции, получающей данные с {stock_market} произошла ошибка: {e}\n' \
                   f'response: {response}\n' \
                   f'response.json: {order_book}\n' \
                   f'--------------------------------------------------------------------------------'
            print(text)

    return orders_sell, orders_buy

code = 40019
coins = ['torn', 'toke', 'moni', 'gm', 'gene', 'bitci', 'rfox', 'polis']
coins = ['eth', 'moni']

list_exchange_not_support = []

for i in coins:
    _get_orders_from_bitget(i, list_exchange_not_support)