name_exchange_where_buy = 'one'
orders_sell = []
currency = 'BTC'




message = f"<a href='{name_exchange_where_buy}'>{orders_sell[0][0]}</a> -> " \
          f"<a href='{name_exchange_where_sell}'>{order_buy[0]}</a>" \
          f" | {currency.upper()}/USDT" \
          f"\n\n" \
          f"📉 Покупка\n\n" \
          f"Объем: {round(need_spent, 2)} USDT -> {round(need_bought, 4)} {currency}" \
          f""