from stock_exchanges.get_data_from_exchanges import all_list_from_all_stock_market
import logging


def _searching_currency_differences(list_with_orders_from_all_stock_market: list) -> list:
    """
    Берем все ордера на покупку и сравниваем с ордерами на продажу.

    Принцип работы.
    Запрашиваем со всех бирж все ордера на покупку и все ордера на продажу.
    Затем в отношении каждой пары бирж (например, биржа 1 и биржа 2), берем каждый ордер на покупку с биржи 1 и берем все ордера на продажу с биржи 2
    Сравниваем, если цена из ордера на продажу больше цены из ордера на покупку (т.е. кто-то готов купить за 100usd, а кто-то готов продать за 95usd, то тогда эту пару вносит в финальный список order_sell_and_orders_by

    Возвращает словарь с order_sell (ордер на покупку) и order_buy (список ордеров на продажу), которые по стоимости ниже ордера на покупку
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
                            order_buy_and_orders_sell['order_buy'] = [order_buy_market, order_buy_link_currency_pair, order_buy_symbol, order_sell_price, order_sell_quantity]
                            order_buy_and_orders_sell['orders_sell'] = orders_sell
                            liet_orders_buy_with_orders_sell.append(order_buy_and_orders_sell)

    return liet_orders_buy_with_orders_sell


def _calculate_margin_filter_order(order_buy_and_orders_sell:dict) -> dict:
    """
    Получаем ордер на покупку и список ордеров на продажу (
    Например:
    ['mexc', 'https://www.mexc.com/ru-RU/exchange/BTC_USDT', 'btc_usdt', '27011.11', '3.5616',
        [['bybit', 'https://www.bybit.com/ru-RU/trade/spot/BTC/USDT', '27005.1', 45.494],
        ['bybit', 'https://www.bybit.com/ru-RU/trade/spot/BTC/USDT', '27005.3', 0.3]]
    )
    Считаем маржу в процентах и долларах и отсеиваем лишние ордера
    Принцип работы:
    берем необходимое количество монет из ордера на продажу и берем столько ордеров на продажу, что бы перекрывало потребность, остальные ордера отсеиываем
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
    price_order_buy = float(order_buy[3])  # цена одной монеты в ордере на покупку
    quantity_order_buy = float(order_buy[4])  # количество монет в ордере на покупку

    orders_sell = order_buy_and_orders_sell['orders_sell']  # ордера на продажу

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

    # считаем маржу в долларах
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


def get_orders_from_exchanges(currency:str) -> list:
    """
    :param currency: Принимает валюту
    Запрашивает ордера на покупку и продажу с бирж
    Сравнивает ордера на покупку и продажу, оставляет только те, которые выгодны
    Считает маржу в процентах и долларах и отсеивает лишние ордера
    Возвращает список словарей, где один словарь это один ордер на покупку и относящиеся к нему ордера на продажу
    """
    list_of_orders = []  # список словарей, где один словарь это один ордер на покупку и относящиеся к нему ордера на продажу

    list_all_list_from_all_stock_market = all_list_from_all_stock_market(currency)  # получаем все значения со всех бирж в отношении выбранной валюты
    orders_sell_and_orders_by = _searching_currency_differences(list_all_list_from_all_stock_market)  # сравниваем все ордеры на покупку со всеми ордерами на продажу
    for order_sell_and_orders_by in orders_sell_and_orders_by: # в отношении каждоого ордера на покупку и относящихся к нему ордеров на продажу
        dict_with_result = _calculate_margin_filter_order(order_sell_and_orders_by)  # считаем маржу в процентах и долларах и отсеиваем лишние ордера
        list_of_orders.append(dict_with_result)  # добавляем в список ордеров

    return list_of_orders
