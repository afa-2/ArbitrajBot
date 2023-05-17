import telebot
import configparser
import time
import logging
from stock_exchanges.get_inf_from_exchanges import get_orders_from_exchanges


def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML", disable_web_page_preview=True)


# Настройки -----------------------------------------------------------------------------------------------------------
# забираем настройки из ini
config = configparser.ConfigParser()
config.read('config.ini')
api = config.get('settings', 'api_key').strip()
# чаты
chats = config.get('settings', 'chats').strip()
chats_list = chats.strip('][').split(', ')
# min profit
min_profit_from_conf = float(config.get('settings', 'min_profit').strip())
# валюты
currencies = config.get('settings', 'currencies').strip()
currencies = currencies.strip('][').split(', ')


# Логирование --------------------------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.ERROR,  # Уровень логирования
    format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("my_log.log"),  # Запись логов в файл
    ]
)


# Программа -----------------------------------------------------------------------------------------------------------
bot = telebot.TeleBot(api)  # запускаем бота

# сообение, что бот запущен
_send_message(bot, chats_list, "Бот запущен")


while True:
    try:
        start_time = time.time()  # Засекаем время начала выполнения кода
        for currency in currencies:  # в отношении каждой валюты
            all_orders = get_orders_from_exchanges(currency)  # получаем все ордера
            if len(all_orders) > 0:  # если ордеров больше 0
                for order in all_orders:  # в отношении каждого ордера
                    order_buy = order['order_buy'] # ордер на покупку
                    orders_sell = order['orders_sell']  # ордера на продажу
                    need_spent = order['need_spent']  # надо потратить
                    need_bought = order['need_bought'] # надо купить монет
                    profit = order['margin'] # профит в процентах
                    profit_in_dol = order['margin_in_dol']  # профит в долларах

                    if profit >= min_profit_from_conf:  # если профит больше или равен профиту из настроек

                        # формируем спсок из всех ордеров на проаджу
                        text_orders_sell = ''
                        for order_sell in orders_sell:  # в отношении каждого ордера на продажу
                            string = f'Цена: {round(order_sell[2], 2)}, кол-во: {round(order_sell[3], 3)}\n'
                            text_orders_sell += string

                        # формируем сообщение
                        message = f"<b>Валютная пара:</b> {currency}/usdt\n\n" \
                                  f"<b>Покупка:</b>\n" \
                                  f"Биржа: <a href='{orders_sell[0][1]}'>{orders_sell[0][0]}</a>\n" \
                                  f"{text_orders_sell}\n" \
                                  f"<b>Продажа:</b>\n" \
                                  f"Биржа: <a href='{order_buy[1]}'>{order_buy[0]}</a>\n" \
                                  f"Цена: {round(order_buy[3], 2)}, кол-во: {round(order_buy[4], 3)}\n\n" \
                                  f"<b>Надо:</b>\n" \
                                  f"потратить: {round(need_spent, 2)}$\n" \
                                  f"что бы купить: {round(need_bought, 4)} монет\n\n" \
                                  f"<b>Тогда прибыль:</b>\n" \
                                  f"В %: {profit}%\n"\
                                  f"В $: {profit_in_dol}$\n"

                        _send_message(bot, chats_list, message)

        end_time = time.time()  # Засекаем время окончания выполнения кода
        elapsed_time = end_time - start_time  # Вычисляем затраченное время
        elapsed_time = round(elapsed_time, 2)

        # text = f"Полный круг. Время выполнения кода: {elapsed_time} секунд"
        # for chat in chats_list:
        #     if len(chat) > 0:
        #         bot.send_message(chat, text, parse_mode="HTML")

    except Exception as e:
        logging.error(e)
        _send_message(bot, chats_list, "Упс. Какая-то ошибочка")


bot.infinity_polling()


