import telebot
import configparser
import time
import logging
from stock_exchanges.get_inf_from_exchanges import get_orders_from_exchanges


def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML")


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
            for order in all_orders:  # в отношении каждого ордера

                # профит
                data = order[4]
                min_profit = min(data, key=lambda x: x[-1])[-1]
                max_profit = max(data, key=lambda x: x[-1])[-1]

                if max_profit >= min_profit_from_conf: # если профит больше или равен профиту из настроек
                    text_orders_sell = ''
                    for order_sell in order[4]:
                        string = f'Цена: {order_sell[1]}, кол-во: {order_sell[2]}\n'
                        text_orders_sell += string

                    if min_profit != max_profit:
                        text_profit = f'<b>Профит:</b> {min_profit}-{max_profit}'
                    else:
                        text_profit = f'<b>Профит:</b> {min_profit}'

                    message = f"-------------------\n" \
                              f"<b>Валютная пара:</b> {currency}/usdt\n\n" \
                              f"<b>Покупка:</b>\n" \
                              f"Биржа: {order[4][0][0]}\n" \
                              f"{text_orders_sell}\n" \
                              f"<b>Продажа:</b>\n" \
                              f"Биржа: {order[0]}\n" \
                              f"Цена: {order[2]}, кол-во: {order[3]}\n\n" \
                              f"{text_profit}\n"\
                              f"--------------------"

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
        _send_message(bot, chats_list, "Какая-то ошибочка")


bot.infinity_polling()


