from stock_exchanges.stock_exchanges import _get_orders_from_binance

orders_buy, orders_sell = _get_orders_from_binance('BTC')
print(orders_buy)
print(orders_sell)