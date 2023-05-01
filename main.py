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
            for order in all_orders:  # в отношении каждого ордера
                print(order)
                # профит в процентах
                data = order[5]
                min_profit = min(data, key=lambda x: x[4])[4]
                max_profit = max(data, key=lambda x: x[4])[4]

                if max_profit >= min_profit_from_conf: # если профит больше или равен профиту из настроек
                    text_orders_sell = ''
                    for order_sell in order[5]:  # в отношении каждого ордера на продажу
                        string = f'Цена: {order_sell[2]}, кол-во: {order_sell[3]}\n'
                        text_orders_sell += string

                    if min_profit != max_profit:
                        text_profit = f'{min_profit}%-{max_profit}%'
                    else:
                        text_profit = f'{min_profit}%'

                    # считаем профит в $
                    cost_coins_ready_to_buy = float(order[3])  # цена монет, которые готовы купить
                    number_of_coins_ready_to_buy = float(order[4])  # количество монет, которые готовы купить

                    we_buy_coins = {'quantity': 0, 'cost': 0}
                    remains_to_buy = number_of_coins_ready_to_buy  # осталось докупить
                    for order_sell in order[5]:  # в отношении каждого ордера на продажу
                        price_coins_ready_to_sell = float(order_sell[2])  # цена за продажу
                        number_of_coins_ready_to_sell = float(order_sell[3])  # количество
                        if number_of_coins_ready_to_sell >= remains_to_buy:  # если количество ордера больше или равно того, что нам требуется
                            we_buy_coins['quantity'] += remains_to_buy  # плюсуем к уже "купленным" ордерам нужное кол-во
                            we_buy_coins['cost'] += price_coins_ready_to_sell * remains_to_buy  # также плюсуем стоимость
                            break  # прекращаем перебор
                        else:  # если количества недостаточно для покрытия ордера на покупку
                            we_buy_coins['quantity'] += number_of_coins_ready_to_sell  # плюсуем к уже "купленным" ордерам все
                            we_buy_coins['cost'] += price_coins_ready_to_sell * number_of_coins_ready_to_sell  # также плюсуем стоимость

                    # считаем, сколько на этом мы заработали
                    if we_buy_coins['quantity'] == number_of_coins_ready_to_buy: # если собрали нужное количество
                        profit_in_dol = (cost_coins_ready_to_buy * number_of_coins_ready_to_buy) - we_buy_coins['cost']
                    else:
                        profit_in_dol = (cost_coins_ready_to_buy * we_buy_coins['quantity']) - we_buy_coins['cost']
                    profit_in_dol = round(profit_in_dol, 2)

                    message = f"<b>Валютная пара:</b> {currency}/usdt\n\n" \
                              f"<b>Покупка:</b>\n" \
                              f"Биржа: <a href='{order[5][0][1]}'>{order[5][0][0]}</a>\n" \
                              f"{text_orders_sell}\n" \
                              f"<b>Продажа:</b>\n" \
                              f"Биржа: <a href='{order[1]}'>{order[0]}</a>\n" \
                              f"Цена: {order[3]}, кол-во: {order[4]}\n\n" \
                              f"<b>Надо:</b>\n" \
                              f"потратить: {round(we_buy_coins['cost'], 2)}$\n" \
                              f"что бы купить: {round(we_buy_coins['quantity'], 4)} монет\n\n" \
                              f"<b>Тогда прибыль:</b>\n" \
                              f"В %: {text_profit}\n"\
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


