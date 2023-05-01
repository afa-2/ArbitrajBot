from stock_exchanges.stock_exchanges import all_list_from_all_stock_market


def _searching_currency_differences(list_with_orders_from_all_stock_market: list) -> list:
    """
    Берем все ордера на покупку и сравниваем с ордерами на продажу.
    Принцип работы.
    Запрашиваем со всех бирж все ордера на покупку и все ордера на проажу.
    Затем в отношении каждой пары бирж (например, биржа 1 и биржа 2), берем каждый ордер на покупку с биржи 1 и берем все ордера на продажу с биржи 2
    Сравниваем, если цена из ордера на продажу больше цены из ордера на покупку (т.е. кто-то готов купить за 100usd, а кто-то готов продать за 95usd, то тогда эту пару вносит в финальный список order_sell_and_orders_by

    Возвращает список из ордеров, где первый идет ордер на покупку, а потом списком все ордера, цена которых ниже цены ордера на покупку
    [ордер на покупку, [ордер на продажу 1, орер на продажу 2, и т.д.]]
    """
    order_sell_and_orders_by = []  # список, одер о готовности купить и к нему ордера о готовности продать

    for stock_market_one in list_with_orders_from_all_stock_market:  # в отношении каждой биржи
        for stock_market_two in list_with_orders_from_all_stock_market:  # в отношении кажой биржи 2, что бы сравнивать (биржа 1 и биржа 2)
            if stock_market_one != stock_market_two:
                all_orders_sell_from_stock_market_one = stock_market_one[1][:3]  # получаем все ордеры на покупку с биржи 1
                all_orders_buy_from_stock_market_two = stock_market_two[0][:3]  # получаем все ордеры на продажу с биржи 2

                first_price_order_sell_from_market_one = all_orders_sell_from_stock_market_one[0]['price']  # ордера на покупку с биржи 1, первое значение цены
                first_price_order_buy_from_market_two = all_orders_buy_from_stock_market_two[0]['price']  # ордера на продажу с биржи 2, первое значение цены

                if first_price_order_sell_from_market_one > first_price_order_buy_from_market_two:  # если максимальная цена предложения о покупке больше чем минимаьная цена предложения о продаже
                    for order_sell in all_orders_sell_from_stock_market_one:  # в отношении каждого ордера о готовности купить
                        order_sell_market = order_sell['stock_market']
                        order_sell_link_currency_pair = order_sell['link_currency_pair']
                        order_sell_symbol = order_sell['symbol']
                        order_sell_price = order_sell['price']
                        order_sell_quantity = order_sell['quantity']

                        orders_buy = []
                        for order_buy in all_orders_buy_from_stock_market_two:  # в отношении каждого ордера о готовности продать
                            order_buy_market = order_buy['stock_market']
                            order_buy_link_currency_pair = order_buy['link_currency_pair']
                            order_buy_symbol = order_buy['symbol']
                            order_buy_price = order_buy['price']
                            order_buy_quantity = order_buy['quantity']

                            if order_sell_price > order_buy_price:
                                # высчитываем маржу в процентах
                                margin = ((float(order_sell_price) - float(order_buy_price))/float(order_buy_price))*100
                                margin = round(margin, 2)

                                # вычисляем маржу в $
                                margin_in_dol = float(order_sell_price) - float(order_buy_price)
                                margin_in_dol = round(margin_in_dol, 2)

                                # добавляем все в список
                                orders_buy.append([order_buy_market, order_buy_link_currency_pair, order_buy_price, order_buy_quantity, margin, margin_in_dol])

                        if len(orders_buy) > 0:
                            order_sell_and_orders_by.append([order_sell_market, order_sell_link_currency_pair, order_sell_symbol, order_sell_price, order_sell_quantity, orders_buy])

    return order_sell_and_orders_by


def get_orders_from_exchanges(currency:str) -> list:
    list_all_list_from_all_stock_market = all_list_from_all_stock_market(currency)  # получаем все значения со всех бирж в отношении выбранной валюты
    order_sell_and_orders_by = _searching_currency_differences(list_all_list_from_all_stock_market)  # сравниваем все ордеры на покупку со всеми ордерами напродажу.

    return order_sell_and_orders_by
